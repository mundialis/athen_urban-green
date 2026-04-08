#!/usr/bin/env python3
# ruff: noqa: PLR0915, PLR2004, D100, TRY003, S701
#
############################################################################
# MODULE:      start_processing
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Run complete service
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################

import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from requests.auth import HTTPBasicAuth

# ### CONFIG ###
# set True to enable automatic time range (from last entry in STAC Catalog)
AUTOMATIC_TIME_RANGE = False
STAC_COLLECTION_URL = "..."  # TODO: Correct Link needs to be added
# for manual time range definition
START_TIME = "2026-03-01"
END_TIME = "2026-03-08"
# Sentinel-2 tile
TILE_ID = "34SGH"
# set max cloud cover
MAX_CLOUD_COVER = 100

# AOI
# By default AOI/bbox is extracted from region
# But bbox can also be defined manually
# Filtering process chain needs to be adjusted accordingly
# -> unset -a flag for i.s2_id.filter
# LONMIN = 23.61
# LATMIN = 37.84
# LONMAX = 23.84
# LATMAX = 38.11

# process chain paths
MAIN_PC_PATH = "processing/templates/"
S2_ID_PROCESS_CHAIN = "process_chain_filter_S2_scenes.json.j2"
MAIN_PROCESS_CHAIN = "process_chain_S2_processing.json.j2"

# variables to set the actinia host, version, and user
GRASS_PROJECT = "athen_urban-green_epsg32634"
ACTINIA_BASEURL = "http://localhost:8088"
ACTINIA_VERSION = "v3"
ACTINIA_URL = ACTINIA_BASEURL + "/api/" + ACTINIA_VERSION
ACTINIA_ENDPOINT = f"{ACTINIA_URL}/locations/{GRASS_PROJECT}/processing_export"
# path to .env file
ENV_PATH = "docker/.env"

# STAC catalog variables
STAC_CATALOG_URL = "http://pycsw:8000/stac/"
STAC_COLLECTION = "urban_green_monitoring"

# STAC item metadata
ASSET_NAMES = "NDVI,NDVI_classified,NDWI,NDWI_classified"
STAC_ITEM_ID_PREFIX = "athen_urban_green"
STAC_ITEM_TITLE = "Urban Green Monitoring Athens"
STAC_ITEM_DESCRIPTION = (
    "NDVI + NDWI raster maps based on Sentinel-2 of Athen for urban green "
    "spaces monitoring."
)


# ### FUNCTIONS ###
# helper function to print formatted JSON using the json module
class HasBeenTerminatedError(Exception):
    """Throw exception class."""

    def __init__(self, request_url: str) -> None:
        """Throw exception."""
        super().__init__(f"The resource <{request_url}> has been terminated.")


# helper function to print formatted JSON using the json module
def print_as_json(data: dict) -> None:
    """Print request as json."""
    print(json.dumps(data, indent=2))


# helper function to verify a request
def verify_request(
    request: requests.Response,
    actinia_auth: HTTPBasicAuth,
    success_code: int = 200,
) -> None:
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
def post_request(
    request_url: str,
    actinia_auth: HTTPBasicAuth,
    process_chain: dict,
) -> tuple[dict, str]:
    """Make a POST request to the Actinia API."""
    # make the POST request to start the processing
    request = requests.post(
        url=request_url,
        auth=actinia_auth,
        json=process_chain,
        timeout=20,
    )
    # check if anything went wrong
    verify_request(request, actinia_auth, 200)
    # get a json-encoded content of the response
    json_response = request.json()
    # get status request URL
    status_request_url = json_response["urls"]["status"]

    return json_response, status_request_url


# function to make a GET request
def get_request(request_url: str, actinia_auth: HTTPBasicAuth) -> dict:
    """Make a GET request to the Actinia API."""
    request = requests.get(
        url=request_url,
        auth=actinia_auth,
        timeout=20,
    )
    verify_request(request, actinia_auth, 200)
    return request.json()


# function to update process chain variables using jinja2 templates
def update_process_chain_variables(
    path_to_template: str,
    pc_variables: dict,
    jinja2_env: Environment,
    *,
    automatic_time_range: bool = False,
) -> dict:
    """Update process chain variables for processing using jinja2 templates."""
    # load the process chain template
    template = jinja2_env.get_template(path_to_template)
    # render process chain template using jinja2
    rendered_pc = template.render(
        automatic_time_range=automatic_time_range,
        **pc_variables,
    )
    return json.loads(rendered_pc)


# ### MAIN ###
def main() -> None:
    """Sentinel-2 scene processing."""
    # check if .env exists
    if not Path(ENV_PATH).is_file():
        raise FileNotFoundError("ERROR: .env file not found. Quitting.")
    # load actinia credentials from .env file
    load_dotenv(dotenv_path=ENV_PATH)
    actinia_user = os.getenv("ACTINIA_USER")
    actinia_password = os.getenv("ACTINIA_PW")
    actinia_auth = HTTPBasicAuth(actinia_user, actinia_password)

    print("======================================")
    print("Start Sentinel-2 processing for Athens...")
    print("Using actinia at:")
    print(ACTINIA_ENDPOINT)
    # adding more variables
    print("======================================")
    print("Filter Sentinel-2 scenes...")

    # fill process chain variables for S2 ID filtering
    pc_variables_filter = {
        "inputs": [
            {"param": "start_time", "value": START_TIME},
            {"param": "end_time", "value": END_TIME},
            {"param": "tile_id", "value": TILE_ID},
            {"param": "cloud_cover", "value": str(MAX_CLOUD_COVER)},
            # {"param": "lonmin", "value": str(LONMIN)},
            # {"param": "lonmax", "value": str(LONMAX)},
            # {"param": "latmin", "value": str(LATMIN)},
            # {"param": "latmax", "value": str(LATMAX)},
            {"param": "stac_collection", "value": str(STAC_COLLECTION_URL)},
        ],
    }

    # initialize jinja2 environment
    jinja2_env = Environment(loader=FileSystemLoader(MAIN_PC_PATH))

    process_chain = update_process_chain_variables(
        S2_ID_PROCESS_CHAIN,
        pc_variables_filter,
        jinja2_env,
        automatic_time_range=AUTOMATIC_TIME_RANGE,
    )

    # send POST request for S2 ID filtering
    _json_response, status_request_url = post_request(
        ACTINIA_ENDPOINT,
        actinia_auth,
        process_chain,
    )

    # wait for a few seconds (otherwise the status request might fail)
    time.sleep(5)

    # implement retry mechanism for status request
    # sometimes it fails with error
    retries = 0
    while retries < 5:
        try:
            # get status response as json
            status_response = get_request(
                status_request_url.replace("https", "http"),
                actinia_auth,
            )
            # extract S2 IDs from status response
            process_results = status_response["process_results"]["s2_ids"][0]
            break
        except (
            requests.exceptions.RequestException,
            KeyError,
            IndexError,
            TypeError,
        ) as e:
            print(f"Error occurred while requesting status: {e}")
            retries += 1
            if retries == 5:
                print("Max retries reached. Quitting.")
                return
            time.sleep(10)
            continue

    # get S2 IDs as dict from actinia response
    process_results_json = json.loads(process_results)
    # if no S2 IDs found, quit
    if len(process_results_json) == 0:
        print("No Sentinel-2 scenes found. Quit.")
        return
    # print found S2 IDs
    print(f"Found <{len(process_results_json)}> Sentinel-2 scene IDs:")
    for result in process_results_json:
        print(f" - {result['s2_id']}")

    print("======================================")
    print("Start Download and Processing...")
    print("======================================")

    pc_variables_processing = {
        "iteration": process_results_json,
        "tile_id": TILE_ID,
        "asset_names": ASSET_NAMES,
        "stac_item_id_prefix": STAC_ITEM_ID_PREFIX,
        "stac_item_title": STAC_ITEM_TITLE,
        "stac_item_description": STAC_ITEM_DESCRIPTION,
        "stac_catalog_url": STAC_CATALOG_URL,
        "stac_collection": STAC_COLLECTION,
    }

    process_chain = update_process_chain_variables(
        MAIN_PROCESS_CHAIN,
        pc_variables_processing,
        jinja2_env,
        automatic_time_range=AUTOMATIC_TIME_RANGE,
    )

    # make the POST request to start the processing
    status_response, status_request_url = post_request(
        ACTINIA_ENDPOINT,
        actinia_auth,
        process_chain,
    )

    # keep polling the status until finished
    while status_response["status"] in {"accepted", "running"}:
        status_response = get_request(
            status_request_url.replace("https", "http"),
            actinia_auth,
        )
        print(f"Polling status: {status_response['status']}")
        print(f"Doing: {status_response['message']}")
        print(f"Status request URL: {status_request_url}")
        print("======================================")
        time.sleep(30)

    print(f"Final status: {status_response['status']}")
    print("Processing finished for:")
    for result in process_results_json:
        print(f" - {result['s2_id']}")
    print("======================================")


if __name__ == "__main__":
    main()
