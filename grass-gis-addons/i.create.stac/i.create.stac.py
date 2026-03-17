#!/usr/bin/env python3
# ruff: noqa: D100
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
import json

import grass.script as grass
import pystac
from rio_stac.stac import create_stac_item


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
            path, roles=["data"], media_type=pystac.MediaType.COG,
        )
        for name, path in zip(asset_names, asset_paths, strict=True)
    }

    # extract datetime from Sentinel-2 ID
    # e.g. S2C_MSIL2A_20251203T092351_N0511_R093_T35SKC_20251203T130213
    s2_datetime = datetime.datetime.strptime(
        s2_id.split("_")[2], "%Y%m%dT%H%M%S",
    ).replace(tzinfo=datetime.timezone.utc)

    # STAC item ID
    stac_item_id = f"{stac_id_prefix}_{s2_id.split("_")[2]}"

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

    # print STAC item as json
    grass.message(json.dumps(item.to_dict(), indent=2))

    # load STAC catalog and collection
    catalog = pystac.Catalog.from_file(f"{stac_catalog}/catalog.json")
    collection = catalog.get_child(stac_collection)

    # add item to collection
    grass.message(
        f"Add STAC item <{item.id}> to collection <{collection.id}> "
        f"of <{catalog.id}>...",
    )
    collection.add_item(item)

    # update temporal and spatial extent of collection
    collection.update_extent_from_items()

    # write out catalog
    catalog.normalize_hrefs(stac_catalog)
    catalog.save(catalog_type=pystac.CatalogType.SELF_CONTAINED)


if __name__ == "__main__":
    options, flags = grass.parser()
    main()
