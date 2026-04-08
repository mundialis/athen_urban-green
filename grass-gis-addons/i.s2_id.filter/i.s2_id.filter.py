#!/usr/bin/env python3
# ruff: noqa: D100, DTZ011, PLR0914
#
############################################################################
# MODULE:      i.s2_id.filter
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Filter Sentinel-2 scenes by time range, AOI, UTM tile ID
# and cloud cover.
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################
#
# %module
# % description: Filter S2 scenes by time range, AOI, tile ID and cloud cover.
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

# %option
# % key: stac_collection
# % description: URL to STAC collection for retrieving start time
# % required: no
# % type: string
# %end

# %flag
# % key: a
# % description: Use current region as AOI for filtering S2 scenes
# %end

# %flag
# % key: t
# % description: Retrieve start time from last entry in STAC collection
# %end

# %rules
# % collective: lonmin,lonmax,latmin,latmax
# % requires: -t,stac_collection
# %end

import datetime
import json
import sys

import grass.script as grass
import pystac
from eodag import EODataAccessGateway


def main() -> None:
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
    stac_collection = options["stac_collection"]
    a = flags["a"]
    t = flags["t"]

    # get bbox from region (must have been set before)
    if a:
        bbox_ll = grass.parse_command(
            "g.region",
            format="json",
            flags="b",
            quiet=True,
        )
        lonmin = bbox_ll["ll_w"]
        lonmax = bbox_ll["ll_e"]
        latmin = bbox_ll["ll_s"]
        latmax = bbox_ll["ll_n"]

    if t:
        # get end date of temporal extent of STAC collection
        collection = pystac.Collection.from_file(stac_collection)
        temp_extent = collection.extent.temporal.intervals
        end_stac_extent = temp_extent[0][1]
        # check if end time is None
        if end_stac_extent is None:
            # stop processing
            grass.fatal("No end time found in STAC collection")

        # overwrite start and end date for filtering range
        start_tmp = end_stac_extent + datetime.timedelta(days=1)
        start = start_tmp.strftime("%Y-%m-%d")
        end = datetime.date.today().strftime("%Y-%m-%d")

    # define search criteria
    search_criteria = {
        "provider": "cop_dataspace",
        "collection": "S2_MSI_L2A",
        "start": start,
        "end": end,
        "geom": {
            "lonmin": float(lonmin),
            "latmin": float(latmin),
            "lonmax": float(lonmax),
            "latmax": float(latmax),
        },
        "eo:cloud_cover": cloud_cover,
    }

    # add tile ID to search criteria
    if tile_id:
        search_criteria["grid:code"] = f"MGRS-{tile_id}"

    # initialize EODataAccessGateway
    dag = EODataAccessGateway()

    # search for S2 scenes matching the criteria
    all_products = dag.search_all(**search_criteria)

    # extract S2 IDs from search results
    s2_ids = [
        all_products[i].properties["id"] for i in range(len(all_products))
    ]

    # format result
    result = [
        {"s2_id": s2_id, "date": date.strftime("%Y-%m-%d"), "year": year}
        for s2_id in s2_ids
        for date in [
            datetime.datetime.strptime(s2_id.split("_")[2], "%Y%m%dT%H%M%S")
        ]
        for year in [date.year]
    ]

    # add year
    # write result to stdout
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
