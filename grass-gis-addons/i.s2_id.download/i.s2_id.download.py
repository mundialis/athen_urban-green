#!/usr/bin/env python3
#
############################################################################
#
# MODULE:      i.s2_id.download
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Downloads S2 scene from Copernicus Data Space.
# COPYRIGHT:   (C) 2024 by mundialis GmbH & Co. KG and the GRASS
#              Development Team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################

# %module
# % description: Downloads S2 scene from Copernicus Data Space by given scene ID.
# % keyword: raster
# % keyword: Sentinel-2
# % keyword: eodag
# %end

# %option
# % key: s2_id
# % description: ID of Sentinel-2 scene, which shall be downloaded
# % required: yes
# %end

# %option
# % key: download_dir
# % description: path to download directory
# % required: yes
# %end

import os

from datetime import datetime, timedelta

from eodag import EODataAccessGateway
from eodag.crunch import FilterProperty

import grass.script as grass


def main():
    # set Sentinel-2 scene ID
    # example: 'S2B_MSIL2A_20240109T103329_N0510_R108_T32ULB_20240109T114910'
    id = options["s2_id"]

    # set download directory
    download_dir = options["download_dir"]

    # check if the directory exists
    if not os.path.exists(download_dir):
        # create the directory
        os.makedirs(download_dir)
        print(f"Directory '{download_dir}' created.")

    # create EODataAccessGateway
    dag = EODataAccessGateway()

    # set copernicus data space as preferred download provider
    dag.set_preferred_provider("cop_dataspace")

    # split ID
    id_split = id.split("_")

    # define search criterias
    # S2 product type: L1C or L2A
    product_type = f"S2_MSI_{id_split[1][3:]}"

    search_criteria = {
        "productType": product_type,
        "id": id,
    }

    # search products
    all_products = dag.search_all(**search_criteria)

    # print(f"Got a hand on a total number of {len(all_products)} products.")
    # print(f"All: {all_products}")

    print(f"Filtered products: {all_products}")

    # download S2 scene
    if len(all_products) == 1 and all_products[0].properties["id"] == id:
        print(f"Found product for scene {id}")
        paths = dag.download_all(
            all_products, output_dir=download_dir, extract=False
        )
        print(f"Downloaded to {paths}")
    else:
        print(f"Did not find product for scene {id}")


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
