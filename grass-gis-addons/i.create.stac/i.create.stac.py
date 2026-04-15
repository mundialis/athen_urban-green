#!/usr/bin/env python3
# ruff: noqa: PLR0914, D100, COM812, PTH118, TRY003
#
############################################################################
#
# MODULE:      i.create.stac
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Creates a STAC items from parsed products and posts it to
#              STAC collections
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################
#
# %module
# % description: Creates a STAC item with all parsed bands
# % keyword: raster
# % keyword: STAC
# %end

# %option
# % key: product_paths
# % description: Products to add to STAC item
# % required: yes
# % type: string
# % multiple: yes
# %end

# %option
# % key: product_names
# % description: Products to create STAC items for (e.g. "NDVI, NDWI")
# % required: yes
# % type: string
# % multiple: yes
# %end

# %option
# % key: s2_id
# % description: Sentinel-2 ID used extract date and time
# % required: yes
# % type: string
# %end

# %option
# % key: stac_id_prefix
# % description: Prefix for STAC item ID
# % required: yes
# % type: string
# %end

# %option
# % key: stac_title
# % description: Title for STAC items
# % required: yes
# % type: string
# %end

# %option
# % key: stac_description
# % description: Description for the STAC item
# % required: yes
# % type: string
# %end

# %option
# % key: stac_catalog
# % description: Root folder of STAC catalog
# % required: yes
# % type: string
# %end

# %option
# % key: stac_collections
# % description: Name of STAC collections to add items to
# % required: yes
# % type: string
# %end

import datetime
import os

import grass.script as grass
import pystac
import requests
from rio_stac.stac import create_stac_item


def main() -> None:
    """Create STAC item and add it to catalog."""
    # parse options
    product_paths_str = options["product_paths"]
    product_names_str = options["product_names"]
    s2_id = options["s2_id"]
    stac_id_prefix = options["stac_id_prefix"]
    stac_item_title = options["stac_title"]
    stac_item_description = options["stac_description"]
    stac_catalog = options["stac_catalog"]
    stac_collections_str = options["stac_collections"]

    # convert assets string to list
    product_paths = [asset.strip() for asset in product_paths_str.split(",")]
    product_names = [name.strip() for name in product_names_str.split(",")]
    stac_collections = [
        collection.strip() for collection in stac_collections_str.split(",")
    ]

    # check if number of asset paths and names match and stac collections match
    if not len(product_paths) == len(product_names) == len(stac_collections):
        grass.fatal(
            "Number of asset paths, asset names and stac collections must "
            "match."
        )

    # extract datetime from Sentinel-2 ID
    # e.g. S2C_MSIL2A_20251203T092351_N0511_R093_T35SKC_20251203T130213
    s2_datetime = datetime.datetime.strptime(
        s2_id.split("_")[2],
        "%Y%m%dT%H%M%S",
    ).replace(tzinfo=datetime.timezone.utc)

    # loop over products and create STAC item for each product,
    # then add it to collection and update collection extent
    for product_name, product_path, stac_collection in zip(
        product_names, product_paths, stac_collections, strict=True
    ):

        # STAC item ID
        stac_item_id = f"{stac_id_prefix}_{product_name}_{s2_id.split('_')[2]}"

        # create STAC item
        item = create_stac_item(
            source=product_path,
            id=stac_item_id,
            input_datetime=s2_datetime,
            # assets=bands_assets,
            with_proj=True,
            properties={
                "title": f"{stac_item_title} - {product_name} - {s2_datetime}",
                "description": stac_item_description,
                "S2_ID": s2_id,
            },
        )

        # post STAC item to pycsw
        # url: "http://localhost:8000/stac/collections/urban_green_monitoring/"
        collection_url = os.path.join(
            stac_catalog, "collections", stac_collection
        )
        items_url = os.path.join(collection_url, "items")
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                items_url, headers=headers, json=item.to_dict(), timeout=100
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            grass.fatal(f"Error occurred while posting STAC item: {e}")

        # fetch collection
        collection_json = requests.get(collection_url, timeout=100).json()

        # fetch all items of collection
        try:
            items_json = requests.get(
                f"{collection_url}/items", timeout=100
            ).json()
        except requests.exceptions.RequestException as e:
            grass.fatal(f"Error occurred while fetching items: {e}")

        items_fetched = [
            pystac.Item.from_dict(feat) for feat in items_json["features"]
        ]

        # check if any items were fetched
        if not items_fetched:
            raise ValueError(
                f"No items found for collection <{stac_collection}>"
            )

        # recompute spatial and temporal extent from items
        new_extent = pystac.Extent.from_items(items_fetched).to_dict()
        # update collection json with new extent
        collection_json["extent"] = new_extent

        # update collection with new extent
        try:
            requests.put(
                collection_url,
                json=collection_json,
                headers={"Content-Type": "application/json"},
                timeout=100,
            )
        except requests.exceptions.RequestException as e:
            grass.fatal(f"Error occurred while updating collection: {e}")


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
