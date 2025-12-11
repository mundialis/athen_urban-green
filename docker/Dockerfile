FROM mundialis/actinia:2.12.2

COPY docker/requirements.txt /src/requirements.txt
COPY docker/start.sh /src/start.sh

WORKDIR /src

RUN pip install --no-cache-dir -r /src/requirements.txt

# install GRASS addons
COPY docker/grass_addons_list.csv /src/grass_addons_list.csv
COPY grass-gis-addons /src/grass-gis-addons

# RUN while IFS=, read -r ADDON SERVER; do if [[ $ADDON != "#*" ]]; then unset URL; test -z $SERVER || URL="url=$SERVER"; grass --tmp-project EPSG:4326 --exec g.extension -s extension=$ADDON $URL;fi;done < /src/grass_addons_list.csv

RUN while IFS=, read -r ADDON SERVER; \
    do \
        if [[ $ADDON != "#*" ]]; \
            then unset URL; \
            test -z $SERVER || URL="url=$SERVER"; \
            grass --tmp-project EPSG:4326 --exec g.extension -s extension=$ADDON $URL; \
        fi; \
    done < /src/grass_addons_list.csv

ENTRYPOINT ["/src/start.sh"]