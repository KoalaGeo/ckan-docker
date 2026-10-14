#!/bin/bash
# Entrypoint for the harvester_* services: runs the given ckan command without
# start_ckan.sh (no prerun/uWSGI), after the config the datapusher plugin needs.
#   usage: start_worker.sh ckan -c /srv/app/ckan.ini harvester gather-consumer
set -e

if [[ $CKAN__PLUGINS == *"datapusher"* && -z "$CKAN__DATAPUSHER__API_TOKEN" ]]; then
    # Same as start_ckan.sh + docker-entrypoint.d/01_setup_datapusher.sh: the plugin won't
    # load without a token, so set a placeholder, then replace it with a real one so
    # resources created by harvests are still pushed to the DataStore.
    ckan config-tool "$CKAN_INI" "ckan.datapusher.api_token=xxx" > /dev/null
    token=$(ckan -c "$CKAN_INI" user token add "${CKAN_SYSADMIN_NAME:-ckan_admin}" datapusher-worker 2>/dev/null | tail -n 1 | tr -d '\t')
    ckan config-tool "$CKAN_INI" "ckan.datapusher.api_token=$token" > /dev/null
fi

exec "$@"
