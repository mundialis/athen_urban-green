#!/usr/bin/env python3
# ruff: noqa: D100, PTH118, PTH208
#
############################################################################
# MODULE:      remove_data
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Remove downloaded S2 scenes
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
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
# % required: no
# % type: string
# %end

# %option
# % key: end_time
# % description: End time for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: tile_id
# % description: S2 tile ID for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: cloud_cover
# % description: Maximum cloud cover for filtering S2 scenes
# % required: no
# % answer: 100
# % type: string
# %end

# %option
# % key: lonmin
# % description: Minimum longitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: lonmax
# % description: Maximum longitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: latmin
# % description: Minimum latitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %option
# % key: latmax
# % description: Maximum latitude for filtering S2 scenes
# % required: no
# % type: string
# %end

# %flag
# % key: a
# % description: Keep downloaded data in the download directory
# %end

# %rules
# % collective: lonmin,lonmax,latmin,latmax
# %end

import sys
import json
import grass.script as grass
from eodag import EODataAccessGateway


def main():
    """Filter S2 scenes."""
    # Get options
    start = options["start_time"]
    end = options["end_time"]
    tile_id = options["tile_id"]
    cloud_cover = options["cloud_cover"]
    lonmin = options["lonmin"]
    lonmax = options["lonmax"]
    latmin = options["latmin"]
    latmax = options["latmax"]
    a = flags["a"]

    # get bbox from region (must have been set before)
    if a:
        bbox_ll = grass.parse_command(
            "g.region", format="json", flags="b", quiet=True
        )
        lonmin = bbox_ll["ll_w"]
        lonmax = bbox_ll["ll_e"]
        latmin = bbox_ll["ll_s"]
        latmax = bbox_ll["ll_n"]

    # define search criteria
    search_criteria = {
        "productType": "S2MSI2A",
        "start": start,
        "end": end,
        "geom": {
            "lonmin": float(lonmin),
            "latmin": float(latmin),
            "lonmax": float(lonmax),
            "latmax": float(latmax),
        },
        "cloudCover": cloud_cover,
    }

    # add tile ID to search criteria
    if tile_id:
        search_criteria["tileIdentifier"] = tile_id

    # initialize EODataAccessGateway
    dag = EODataAccessGateway()

    # search for S2 scenes matching the criteria
    all_products = dag.search_all(**search_criteria)

    # extract S2 IDs from search results
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
