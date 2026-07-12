## Description

*i.create.stac* creates and publishes STAC items for raster products,
deriving the item timestamp from a Sentinel-2 scene identifier. Each
product is posted to the configured STAC collection endpoint and the
collection extent is recomputed from all items after insertion.

## Notes

- The number of values in **product_paths**, **product_names**, and
  **stac_collections** must be identical.
- For each product, one STAC item is generated and posted to
  `<stac_catalog>/collections/<collection>/items`.
- After publishing an item, the module fetches all collection items and
  updates the collection extent accordingly.
- The generated item ID format is
  `<stac_id_prefix>_<product_name>_<s2_datetime_token>`.

## EXAMPLES

```sh
i.create.stac \
    product_paths="data/ndvi.tif,data/ndwi.tif" \
    product_names="NDVI,NDWI" \
    s2_id="S2C_MSIL2A_20251203T092351_N0511_R093_T35SKC_20251203T130213" \
    stac_id_prefix="s2_indices" \
    stac_title="Sentinel-2 indices" \
    stac_description="Sentinel-2 NDVI and NDWI products for Athens urban green monitoring" \
    stac_catalog="http://localhost:8000/stac" \
    stac_collections="s2_ndvi,s2_ndwi"
```

## Python dependencies

This module relies on Python packages `pystac`, `requests`, and
`rio-stac`.

## SEE ALSO

- [pystac documentation](https://pystac.readthedocs.io/en/stable/)
- [rio-stac documentation](https://rio-stac.readthedocs.io/en/stable/)

## AUTHORS

Jonas Pischke, [mundialis GmbH & Co. KG](https://www.mundialis.de/),
Germany
