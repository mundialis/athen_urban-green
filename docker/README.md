# Docker setup

## Local setup
All of the following must be launched from within the `docker` directory.

### First time only
* Create an **`.env` file** with the following structure in the `docker` directory:
```yaml
ACTINIA_USER=<USER>
ACTINIA_PW=<PASSWORD>
EODAG_USER=<CDSE_USER>
EODAG_PW=<CDSE_PASSWORD>
```

### Build and start docker
Note: [docker-compose-plugin](https://docs.docker.com/compose/install/linux/) needs to be installed

build:
```bash
docker compose -f docker-compose.yml -p athen_urban-green build
```

To completely rebuild all images when changes are made, the build command should be extended with the `--no-cache` parameter.

start:
```bash
docker compose -f docker-compose.yml -p athen_urban-green up
```

stop:
```bash
docker compose -f docker-compose.yml -p athen_urban-green down
```

#### Access actinia (in Browser)
```python
# e.g., to see the version
http://localhost:8088/api/v3/version

# or to list locations
http://localhost:8088/api/v3/locations
```

#### Enter running docker container
``` bash
# e.g.
docker exec -it athen_urban-green-actinia-1 /bin/sh
```