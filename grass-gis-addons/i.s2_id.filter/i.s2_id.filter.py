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
# %module
# % description: Filter S2 scenes by time range, AOI, tile ID + cloud cover.
# % keyword: raster
# % keyword: Sentinel-2
# % keyword: eodag
# %end

# %option
# % key: start_time
# % description: Start time for filtering S2 scenes
# % required: yes
# %end

# %option
# % key: end_time
# % description: End time for filtering S2 scenes
# % required: yes
# %end

# %option
# % key: tile_id
# % description: S2 tile ID for filtering S2 scenes
# % required: yes
# %end

# %option
# % key: cloud_cover
# % description: Maximum cloud cover for filtering S2 scenes
# % required: no
# %end

# %option
# % key: lonmin
# % description: Minimum longitude for filtering S2 scenes
# % required: yes
# %end

# %option
# % key: lonmax
# % description: Maximum longitude for filtering S2 scenes
# % required: yes
# %end

# %option
# % key: latmin
# % description: Minimum latitude for filtering S2 scenes
# % required: yes
# %end

# %option
# % key: latmax
# % description: Maximum latitude for filtering S2 scenes
# % required: yes
# %end

import sys
import json
import grass.script as grass
from eodag import EODataAccessGateway


def main():
    # Get options
    start = str(options["start_time"])
    end = str(options["end_time"])
    tile_id = str(options["tile_id"])
    cloud_cover = int(options["cloud_cover"])
    lonmin = float(options["lonmin"])
    lonmax = float(options["lonmax"])
    latmin = float(options["latmin"])
    latmax = float(options["latmax"])

    # define search criteria
    search_criteria = {
        "productType": "S2MSI2A",
        "start": start,
        "end": end,
        "tileIdentifier": tile_id,
        "geom": {
            "lonmin": lonmin,
            "latmin": latmin,
            "lonmax": lonmax,
            "latmax": latmax,
        },
        "cloudCover": cloud_cover,
    }

    # initialize EODataAccessGateway
    dag = EODataAccessGateway()

    # search for S2 scenes matching the criteria
    all_products = dag.search_all(**search_criteria)

    s2_ids = [
        all_products[i].properties["id"] for i in range(len(all_products))
    ]

    # format result
    result = {f"S2_ID_{i+1}": id_value for i, id_value in enumerate(s2_ids)}
    # write result to stdout
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
