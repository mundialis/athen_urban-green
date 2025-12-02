FROM mundialis/actinia:2.12.2

# RUN pip install grass-gis-helpers pandas pillow reportlab

COPY docker/start.sh /src/start.sh

WORKDIR /src

ENTRYPOINT ["/src/start.sh"]