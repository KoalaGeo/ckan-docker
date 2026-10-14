"""
Add the Solr fields ckanext-spatial's "solr-bbox" search backend needs.

ckan-docker uses the standard ckan/ckan-solr image (SOLR_IMAGE_VERSION in .env). Its
"-spatial" variant only differs by adding these five fields; adding them here through
Solr's Schema API means we don't depend on that variant's tag. Without them, CKAN's
catch-all `*` field would index the bbox values as *strings*, and spatial searches
would silently return wrong results.

Idempotent: fields that already exist are left alone. Run by start_ckan.sh (as a .py
file in /docker-entrypoint.d) on every start of the CKAN web container.
"""
import json
import os
import sys
import urllib.error
import urllib.request

FIELDS = ["minx", "maxx", "miny", "maxy", "bbox_area"]

plugins = os.environ.get("CKAN__PLUGINS", "").split()
if "spatial_query" not in plugins:
    print("[solr-spatial] spatial_query not enabled, skipping")
    sys.exit(0)

solr = os.environ.get("CKAN_SOLR_URL", "http://solr:8983/solr/ckan").rstrip("/")


def field_exists(name):
    try:
        urllib.request.urlopen(f"{solr}/schema/fields/{name}?wt=json", timeout=10).read()
        return True
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise


try:
    missing = [f for f in FIELDS if not field_exists(f)]
    if not missing:
        print("[solr-spatial] bbox fields already present")
        sys.exit(0)
    body = json.dumps({
        "add-field": [
            {"name": f, "type": "float", "indexed": True, "stored": True} for f in missing
        ]
    }).encode()
    req = urllib.request.Request(
        f"{solr}/schema?wt=json", data=body, headers={"Content-Type": "application/json"}
    )
    result = json.loads(urllib.request.urlopen(req, timeout=30).read())
    if result.get("errors") or result.get("error"):
        raise RuntimeError(result)
    print(f"[solr-spatial] added Solr fields: {', '.join(missing)}")
except Exception as e:  # noqa: BLE001
    # Don't block CKAN starting; spatial search is the only thing affected
    print(f"[solr-spatial] WARNING: could not add bbox fields ({e}); spatial search "
          f"will not work until they exist")
