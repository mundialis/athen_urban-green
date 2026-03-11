#!/usr/bin/env python3
# ruff: noqa: D100, PTH118, PTH208
############################################################################
# MODULE:      remove_data
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Remove downloaded S2 scenes
#
# SPDX-FileCopyrightText: (c) 2025 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################
#
import sys
import json
from eodag import EODataAccessGateway

def main():

    START = "2025-12-01"
    END = "2025-12-12"
    TILE_ID = "34SGH"
    CLOUD_COVER = 90

    search_criteria = {
    "productType": "S2MSI2A",
    "start": START,
    "end": END,
    "tileIdentifier": TILE_ID,
    "geom": {"lonmin": 23.61, "latmin": 37.84, "lonmax": 23.84, "latmax": 38.11},
    "cloudCover": CLOUD_COVER,
    }

    dag = EODataAccessGateway()

    all_products = dag.search_all(**search_criteria)
    s2_ids = [all_products[i].properties["id"] for i in range(len(all_products))]
 

    result = {f"S2_ID_{i+1}": id_value for i, id_value in enumerate(s2_ids)}
    sys.stdout.write(json.dumps(result))    



if __name__ == "__main__":
    main()