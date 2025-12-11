#!/bin/sh
########################################################################
#
# MODULE:       start.sh
#
# AUTHOR(S):    Victoria-Leandra Brunn, Julia Haas
#               
# PURPOSE:      This script starts actinia
#
# SPDX-FileCopyrightText: (c) 2025 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
########################################################################

# create default GRASS project
[ ! -d "/actinia_core/grassdb/latlong_wgs84" ] && grass --text -e -c 'EPSG:4326' /actinia_core/grassdb/latlong_wgs84

# create actinia user
actinia-user create -u "$ACTINIA_USER" -w "$ACTINIA_PW" -r superadmin -g superadmin -c 100000000000 -n 1000 -t 31536000
actinia-user update -u "$ACTINIA_USER" -w "$ACTINIA_PW"
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia-user: $status"
  exit $status
fi

ACTINIA_RUNNING_SINCE=$(date)
export ACTINIA_RUNNING_SINCE
ACTINIA_DOCKER_VERSION=$(cat /actinia-docker-version.txt)
#OS_VERSION=$(cat /etc/os-release | grep PRETTY | cut -d "=" -f 2 | cut -d '"' -f2)
OS_VERSION=$(grep PRETTY /etc/os-release| cut -d "=" -f 2 | cut -d '"' -f2)
export ACTINIA_ADDITIONAL_VERSION_INFO="actinia_docker_version:$ACTINIA_DOCKER_VERSION|os_version:$OS_VERSION"

# start actinia
gunicorn -b 0.0.0.0:8088 -w 8 --access-logfile=- -k gthread actinia_core.main:flask_app
status=$?
if [ $status -ne 0 ]; then
  echo "Failed to start actinia_core/main.py: $status"
  exit $status
fi
