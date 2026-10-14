FROM ckan/ckan-base:2.11

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples
# - Make sure to add the plugins to CKAN__PLUGINS in the .env file
#
# Versions are pinned to release tags so rebuilds are reproducible.
USER root

### Harvester ###  (needs the harvester_* services in docker-compose.yml)
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-harvest.git@v1.6.3#egg=ckanext-harvest'

### DCAT ###
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-dcat.git@v2.4.4#egg=ckanext-dcat'

### Spatial ###  (spatial search uses the Solr bbox fields, see docker-entrypoint.d/02_solr_spatial_fields.py)
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-spatial.git@v2.3.2#egg=ckanext-spatial'

### Geoview ###
RUN pip3 install -e 'git+https://github.com/ckan/ckanext-geoview.git@v0.3.2#egg=ckanext-geoview'

# Same ownership the base image uses for the source dir and Python packages
RUN chown -R ckan:ckan-sys ${SRC_DIR} && chown -R ckan-sys:ckan-sys /usr/local

# Entrypoint for the harvester_* services in docker-compose.yml
COPY --chown=ckan-sys:ckan-sys --chmod=755 setup/start_worker.sh ${APP_DIR}/start_worker.sh

# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/

# Apply any patches needed to CKAN core or any of the built extensions (not the
# runtime mounted ones)
COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches

USER ckan

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done
