FROM mundialis/actinia:2.12.2

COPY docker/requirements.txt /src/requirements.txt
COPY docker/start.sh /src/start.sh

WORKDIR /src

RUN pip install --no-cache-dir -r /src/requirements.txt

ENTRYPOINT ["/src/start.sh"]