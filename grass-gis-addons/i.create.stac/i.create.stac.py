#!/usr/bin/env python3
# ruff: noqa: PLR0914, D100, COM812, PTH118, TRY003
#
############################################################################
#
# MODULE:      i.create.stac
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Creates a STAC item with all parsed bands as assets and adds
#              it to the specified STAC catalog and collection.
# COPYRIGHT:   (C) 2024 by mundialis GmbH & Co. KG and the GRASS
#              Development Team
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
# % key: asset_paths
# % description: Assets to add to STAC item
# % required: yes
# % type: string
# % multiple: yes
# %end

# %option
# % key: asset_names
# % description: Assets to add to STAC item
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
# % description: Prefix for the STAC item ID
# % required: yes
# % type: string
# %end

# %option
# % key: stac_title
# % description: Title for the STAC item
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
# % key: stac_collection
# % description: Name of STAC collection
# % required: yes
# % type: string
# %end

import datetime
import os

import grass.script as grass
import pystac
import requests
from rio_stac.stac import create_stac_item


def add_item_unique(collection: pystac.Collection, item: pystac.Item) -> None:
    """Add item to collection if it doesn't already exist."""
    existing_ids = {i.id for i in collection.get_all_items()}
    if item.id not in existing_ids:
        collection.add_item(item)
    else:
        grass.message(
            f"STAC item <{item.id}> already exists in collection"
            f"<{collection.id}>."
        )
        grass.message("Not adding duplicate item.")


def main() -> None:
    """Create STAC item and add it to catalog."""
    # parse options
    asset_paths_str = options["asset_paths"]
    asset_names_str = options["asset_names"]
    s2_id = options["s2_id"]
    stac_id_prefix = options["stac_id_prefix"]
    stac_item_title = options["stac_title"]
    stac_item_description = options["stac_description"]
    stac_catalog = options["stac_catalog"]
    stac_collection = options["stac_collection"]

    # convert assets string to list
    asset_paths = [asset.strip() for asset in asset_paths_str.split(",")]
    asset_names = [name.strip() for name in asset_names_str.split(",")]

    # create dict from asset_paths and asset_names
    bands_assets = {
        name: pystac.Asset(
            path,
            roles=["data"],
            media_type=pystac.MediaType.COG,
        )
        for name, path in zip(asset_names, asset_paths, strict=True)
    }

    # extract datetime from Sentinel-2 ID
    # e.g. S2C_MSIL2A_20251203T092351_N0511_R093_T35SKC_20251203T130213
    s2_datetime = datetime.datetime.strptime(
        s2_id.split("_")[2],
        "%Y%m%dT%H%M%S",
    ).replace(tzinfo=datetime.timezone.utc)

    # STAC item ID
    stac_item_id = f"{stac_id_prefix}_{s2_id.split('_')[2]}"

    # create STAC item
    item = create_stac_item(
        source=asset_paths[0],
        id=stac_item_id,
        input_datetime=s2_datetime,
        assets=bands_assets,
        with_proj=True,
        properties={
            "title": f"{stac_item_title} - {s2_datetime}",
            "description": stac_item_description,
            "S2_ID": s2_id,
        },
    )

    # post STAC item to pycsw
    # url: "http://localhost:8000/stac/collections/urban_green_monitoring/"
    collection_url = os.path.join(stac_catalog, "collections", stac_collection)
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

    # items_fetched = []
    # for feat in items_json["features"]:
    #     items_fetched.append(pystac.Item.from_dict(feat))
    items_fetched = [
        pystac.Item.from_dict(feat) for feat in items_json["features"]
    ]

    # check if any items were fetched
    if not items_fetched:
        raise ValueError(f"No items found for collection <{stac_collection}>")

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
