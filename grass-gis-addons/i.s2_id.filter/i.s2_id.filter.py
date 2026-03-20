#!/usr/bin/env python3
# ruff: noqa: D100, PTH118, PTH208
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
# % key: stac_catalog
# % description: Name of STAC catalog for getting start time
# % required: no
# % type: string
# %end

# %flag
# % key: a
# % description: Use current region as AOI for filtering S2 scenes
# %end

# %flag
# % key: t
# % description: Get start time from last entry in STAC catalog
# %end

# %rules
# % collective: lonmin,lonmax,latmin,latmax
# % requires: -t,stac_catalog
# %end

import sys
import json
import datetime
import grass.script as grass
from eodag import EODataAccessGateway
import pystac


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
    stac_catalog = options["stac_catalog"]
    a = flags["a"]
    t = flags["t"]

    # get bbox from region (must have been set before)
    if a:
        bbox_ll = grass.parse_command(
            "g.region", format="json", flags="b", quiet=True
        )
        lonmin = bbox_ll["ll_w"]
        lonmax = bbox_ll["ll_e"]
        latmin = bbox_ll["ll_s"]
        latmax = bbox_ll["ll_n"]

    if t:
        # get end date of temporal extent of STAC collection
        collection = pystac.Collection.from_file(stac_catalog)
        temp_extent = collection.extent.temporal.intervals
        end_stac = temp_extent[0][1]
        # check if end time is None
        if end_stac is None:
            # stop processing
            grass.fatal("No end time found in STAC collection")

        # overwrite start and end date for filtering range
        start = end_stac.strftime("%Y-%m-%d")
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
    result = {f"S2_ID_{i+1}": id_value for i, id_value in enumerate(s2_ids)}
    # write result to stdout
    sys.stdout.write(json.dumps(result))

if __name__ == "__main__":
    options, flags = grass.parser()
    main()
