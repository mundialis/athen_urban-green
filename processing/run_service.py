#!/usr/bin/env python3
############################################################################
# MODULE:      start_processing
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Run complete service
#
# SPDX-FileCopyrightText: (c) 2025 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################

import json
import time
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth


### CONFIG ###

# Filtering parameters
START_TIME = "2025-12-01"
END_TIME = "2025-12-05"
TILE_ID = "34SGH"
MAX_CLOUD_COVER = 100 # set max cloud cover
# AOI
# ToDO get automatically from vector (is in grass project) 
# maybe directly in addon (runs in grass anyways)
LONMIN = 23.61
LATMIN = 37.84
LONMAX = 23.84
LATMAX = 38.11

# process chain paths
MAIN_PC_PATH = "templates/"
S2_ID_PROCESS_CHAIN = "pc_filter_S2_v2.json"
MAIN_PROCESS_CHAIN = "pc_loop_ids.json"

# variables to set the actinia host, version, and user
grass_project = "athen_urban-green_epsg32634"
actinia_baseurl = "http://localhost:8088"
actinia_version = "v3"
actinia_url = actinia_baseurl + "/api/" + actinia_version
# Todo: Get credentials from .env
actinia_auth = HTTPBasicAuth("actinia", "actinia")
actinia_endpoint = f"{actinia_url}/locations/{grass_project}/processing_export"

### functions ###

# helper function to print formatted JSON using the json module
class HasBeenTerminatedError(Exception):
    """Throw exception class."""

    def __init__(self, request_url) -> None:
        """Throw exception."""
        super().__init__(f"The resource <{request_url}> has been terminated.")

# helper function to print formatted JSON using the json module
def print_as_json(data) -> None:
    """Print request as json."""
    print(json.dumps(data, indent=2))


# helper function to verify a request
def verify_request(request, success_code=200) -> None:
    """Verify the request."""
    if request.status_code != success_code:
        print(
            "ERROR: actinia processing failed with status code "
            f"{request.status_code}!",
        )
        print("See errors below:")
        print_as_json(request.json())
        request_url = request.json()["urls"]["status"]
        requests.delete(url=request_url, auth=actinia_auth, timeout=20)
        raise HasBeenTerminatedError(request_url)

# function to make a POST request
def post_request(request_url, actinia_auth, process_chain):
    # make the POST request to start the processing
    request = requests.post(
        url=request_url, auth=actinia_auth, json=process_chain, timeout=20,
    )
    # check if anything went wrong
    verify_request(request, 200)
    # get a json-encoded content of the response
    json_response = request.json()   
    # get status request URL
    status_request_url = json_response["urls"]["status"]

    return json_response, status_request_url

# function to make a GET request
def get_request(request_url, actinia_auth):
    request = requests.get(
            url=request_url, auth=actinia_auth,
            timeout=20,
        )
    verify_request(request, 200)
    json_response = request.json()
    return json_response

### MAIN ###
def main():
    print("======================================")
    print("Start Sentinel-2 processing for Athens...")
    print("Using actinia at:")
    print(actinia_endpoint)
    # adding more variables
    print("======================================")
    print("Filter Sentinel-2 scenes...")

    # open process chain for S2 ID filtering
    with open(MAIN_PC_PATH + S2_ID_PROCESS_CHAIN, encoding="utf-8") as f:
        process_chain = json.load(f)

    # insert search parameters into process chain
    # variables need to be strings for actinia process chain!!!
    process_chain["list"][0]["inputs"][0]["value"] = START_TIME
    process_chain["list"][0]["inputs"][1]["value"] = END_TIME
    process_chain["list"][0]["inputs"][2]["value"] = TILE_ID
    process_chain["list"][0]["inputs"][3]["value"] = str(MAX_CLOUD_COVER)
    process_chain["list"][0]["inputs"][4]["value"] = str(LONMIN)
    process_chain["list"][0]["inputs"][5]["value"] = str(LONMAX)
    process_chain["list"][0]["inputs"][6]["value"] = str(LATMIN)
    process_chain["list"][0]["inputs"][7]["value"] = str(LATMAX)

    # send POST request for S2 ID filtering
    _json_response, status_request_url = post_request(actinia_endpoint, actinia_auth, process_chain)

    # wait for a few seconds (otherwise the status request might fail)
    time.sleep(5)

    # get status response as json
    status_response = get_request(status_request_url.replace("https", "http"), actinia_auth)

    # extract S2 IDs from status response
    # ToDo: in case of error/no scenes, handle it
    stdout = status_response["process_log"][0]["stdout"]
    S2_scenes_dict = json.loads(stdout)
    print(f"Found <{len(S2_scenes_dict)}> Sentinel-2 scene IDs:")
    for _i, s2_id in S2_scenes_dict.items():
        print(f" - {s2_id}")

    print("======================================")
    print("Start Download and Processing...")
    print("======================================")

    # load the main process chain
    with open(MAIN_PC_PATH + MAIN_PROCESS_CHAIN, encoding="utf-8") as f:
        process_chain = json.load(f)

    # insert Sentinel-2 IDs into the process chain
    process_chain["list"][1]["inputs"][0]["value"] = list(S2_scenes_dict.values())

    # make the POST request to start the processing
    status_response, status_request_url = post_request(actinia_endpoint, actinia_auth, process_chain)

    # keep polling the status until finished
    while status_response["status"] in {"accepted", "running"}:
        status_response = get_request(status_request_url.replace("https", "http"), actinia_auth)
        print(f"Polling status: {status_response['status']}")        
        print(f"Doing: {status_response['message']}")
        # print(f"Status request URL: {status_request_url}")
        print("======================================")
        time.sleep(30)

    print(f"Final status: {status_response['status']}")
    print(f"Processing finished for:")
    for s2_id in list(S2_scenes_dict.values()):
        print(f" - {s2_id}")
    print("======================================")


    # print output URLs
    # Probably not necessary for final script
    # Useful for dev status
    for tif in status_response["urls"]["resources"]:
        print(f"{Path(tif).name}: {tif.replace('https', 'http')}")

if __name__ == "__main__":
    main()