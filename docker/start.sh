#!/bin/sh

# # create default projects in mounted (!) directory
# [ ! -d "/actinia_core/grassdb/latlong_wgs84" ] && grass --text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84

actinia-user create -u $ACTINIA_USER -w $ACTINIA_PW -r superadmin -g superadmin -c 100000000000 -n 1000 -t 31536000
actinia-user update -u $ACTINIA_USER -w $ACTINIA_PW
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia-user: $status"
  exit $status
fi

export ACTINIA_RUNNING_SINCE=`date`
ACTINIA_DOCKER_VERSION=`cat /actinia-docker-version.txt`
OS_VERSION=`cat /etc/os-release | grep PRETTY | cut -d "=" -f 2 | cut -d '"' -f2`
export ACTINIA_ADDITIONAL_VERSION_INFO="actinia_docker_version:$ACTINIA_DOCKER_VERSION|os_version:$OS_VERSION"

gunicorn -b 0.0.0.0:8088 -w 8 --access-logfile=- -k gthread actinia_core.main:flask_app
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia_core/main.py: $status"
  exit $status
fi
