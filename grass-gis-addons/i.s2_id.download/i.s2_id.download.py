#!/usr/bin/env python3
# ruff: noqa: D100, PTH118, PTH208
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
# SPDX-FileCopyrightText: (c) 2025 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################

# %module
# % description: Download S2scene from Copernicus Data Space by given scene ID.
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

from pathlib import Path
from eodag import EODataAccessGateway
import grass.script as grass


def main() -> None:
    """Download S2 scene from Copernicus Data Space by given ID."""
    # set Sentinel-2 scene ID
    # example: 'S2B_MSIL2A_20240109T103329_N0510_R108_T32ULB_20240109T114910'
    s2_id = options["s2_id"]

    # set download directory
    download_dir = options["download_dir"]

    # check if the directory exists
    if not Path(download_dir).exists():
        # create the directory
        Path(download_dir).mkdir(parents=True)
        print(f"Directory '{download_dir}' created.")

    # create EODataAccessGateway
    dag = EODataAccessGateway()

    # set copernicus data space as preferred download provider
    dag.set_preferred_provider("cop_dataspace")

    # set search criteria with S2 ID
    # collection not necessary, but speeds up search
    search_criteria = {
        "collection": "S2_MSI_L2A",
        "id": s2_id,
    }

    # search products
    all_products = dag.search_all(**search_criteria)

    # print(f"Got a hand on a total number of {len(all_products)} products.")
    # print(f"All: {all_products}")

    print(f"Filtered products: {all_products}")

    # download S2 scene
    if len(all_products) == 1 and all_products[0].properties["id"] == s2_id:
        print(f"Found product for scene {s2_id}")
        paths = dag.download_all(
            all_products,
            output_dir=download_dir,
            extract=False,
        )
        print(f"Downloaded to {paths}")
    else:
        print(f"Did not find product for scene {s2_id}")


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
