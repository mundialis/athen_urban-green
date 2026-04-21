# Urban Green Monitoring for the Municipality of Athens

This repository contains the processing stack used to monitor urban green areas
in Athens from Earth Observation data (Sentinel-2). It combines:

- an actinia + GRASS GIS processing backend,
- custom GRASS add-ons for Sentinel-2 scene filtering, Sentinel-2 scene download
  and STAC publishing,
- process chain templates for NDVI/NDWI production and classification.

The main output is a set of geospatial products (NDVI/NDWI and classified
versions) plus STAC item updates for catalog publication.

**Note**: This workflow was designed to be integrated with the
[satellite.cityofathens.gr](https://github.com/EOFarm/satellite.cityofathens.gr)
repository. Adding STAC items of processed raster layers to STAC collection
might not work properly if running this worklow independently (needs correct
STAC catalog setup).

## What this workflow does

The workflow in this repository is designed to:

1. Filter Sentinel-2 scenes by date range, AOI, tile id, and cloud cover.
2. Download and import selected scenes into GRASS GIS.
3. Use L2A cloud probability layer to mask out clouds. Cloud proabability threshold is set to 65 %. (Could be changed in `processing/templates/template_S2_download_import.json`). See also [i.sentinel.import](https://grass.osgeo.org/grass-stable/manuals/addons/i.sentinel.import.html).
4. Compute NDVI and NDWI maps.
5. Classify NDVI/NDWI outputs using configured categories for vegetation health
   assessment. The threshold for the categorization is set in `processing/input/index_classification/*classes`.
6. Export raster outputs as COG.
7. Create and publish STAC items to an existing STAC catalog/collection and
   update collection extent metadata.

## Main components

### Custom GRASS Addons

In `./grass-gis-addons/`

- `i.s2_id.filter`
  - Module to query Sentinel-2 metadata via `EODAG` and return scene IDs based
    on filters (date, AOI, tile id, cloud cover).
- `i.s2_id.download`
  - Module to download selected Sentinel-2 scenes using `EODAG`. Imports bands
    using `i.sentinel.import` for processing.
- `i.create.stac`
  - Module to create a STAC item from exported assets and publish it to an
    existing STAC catalog/collection. Also updates collection extents. Uses
    `pystac` and `rio-stac`.

### Scripts

In `./processing/scripts/`

- `create_export_subfolders.py`
  - utility script to create export directory for exported COGs. Directory is
    parsed in process chain template.
- `remove_data.py`
  - cleanup script to remove downloaded Sentinel-2 SAFE files.
- `rename_bands.py`
  - utility script to rename imported raster bands in GRASS location for further
    processing.

### Actinia Process Chains

Jinja2 templates in `./processing/templates/`. Variables are parsed in
`run_service.py` and rendered as JSON before submission to actinia.

- `process_chain_filter_S2_scenes.json.j2`
  - process chain to run `i.s2_id.filter` and return filtered scene ids.
- `process_chain_S2_processing.json.j2`
  - process chain to trigger processing for parsed Sentinel-2 scene ids.

### Actinia Process Templates

Actinia module templates in `./processing/templates/` are used by
`process_chain_S2_processing.json.j2`.

- `template_S2_processing.json`
  - process template to run the main processing steps for a Sentinel-2 scene:
    import, NDVI/NDWI calculation, classification, export, and STAC item
    creation. Calls the following templates for specific steps:
  - `template_S2_download_import.json`
    - process template to download Sentinel-2 scenes using `i.s2_id.download`
      and to import bands using `i.sentinel.import`.
  - `template_calc_NDVI.json`
    - process template to calculate NDVI and categorize it. Exports layers as
      COG.
  - `template_calc_NDWI.json`
    - process template to calculate NDWI and categorize it. Exports layers as
      COG.

### Start service script

- `processing/run_service.py`
  - script to run the whole workflow. Parses parameters, renders process chain
    templates, submits to actinia, and monitors execution.

## How to use this workflow

All Docker commands below are run from the `docker/` directory. For further
docker instructions see `docker/README.md`.

### 1. Configure environment variables

Create `docker/.env` with actinia and [CDSE](https://dataspace.copernicus.eu/)
credentials:

```env
ACTINIA_USER=<your_user>
ACTINIA_PW=<your_password>
EODAG_USER=<your_CDSE_user>
EODAG_PW=<your_CDSE_password>
```

**_Do not commit real credentials in `docker/.env`._**

### 2. Build the image

```bash
docker compose -f docker-compose.yml -p athen_urban-green build
```

For a full rebuild after dependency changes:

```bash
docker compose -f docker-compose.yml -p athen_urban-green build --no-cache
```

### 3. Start containers

For a **Local Setup:** you need to mount a local directory for data export. Add
to volumes for actinia `/path/to/local/export/dir:/src/export_dir`, then:

```bash
docker compose -f docker-compose.yml -p athen_urban-green up
```

### 4. Verify API is up

- Version endpoint: `http://localhost:8088/api/v3/version`
- Locations endpoint: `http://localhost:8088/api/v3/locations`

### 5. Stop containers

```bash
docker compose -f docker-compose.yml -p athen_urban-green down
```

## Run processing

### Run Service

The script in `processing/run_service.py` starts the whole workflow.

From repository root folder:

```bash
python processing/run_service.py
```

#### Script parameters

Important script parameters to adapt before production runs:

**Sentinel-2 query parameters:**

- Time range (`START_TIME`, `END_TIME`, or automatic time range mode) for
  filtering Sentinel-2 scenes.

  **Options:**
  1. **manual time range:** Set `START_TIME` and `END_TIME` e.g. `START_TIME = "2026-04-05"`
  and `END_TIME = "2026-04-10"`
  2. **automatic time range:** Queries given STAC collection `STAC_COLLECTION_URL`
  for latest item and
    sets `START_TIME` accordingly and `END_TIME` to current time. For the
    current settings, the collection `ndvi-ath` is used which is updated with
    each workflow run. Check with names defined in `STAC_COLLECTIONS`.
- `TILE_ID`: Sentinel-2 tile identifier e.g. `34SGH` for Athens area
- `MAX_CLOUD_COVER`: Max. cloud cover threshold
- AOI: By default, the script uses a predefined AOI for Athens in `processing/input/athens_aoi.geojson`.
  - To use a different AOI, replace this file with a new GeoJSON containing the desired AOI geometry (and rebuild image).
  - Or specify a bounding box by setting `LONMIN`, `LONMAX`, `LATMIN`, `LATMAX`.
    - **Note:** Currently `-a` flag is set for i.s2_id.filter in process chain. This enables AOI filtering based on predifined AOI. For bounding box filtering `-a` flag must be removed. --> **TODO**: implement automatic flag removal when bounding box parameters are set.



**actinia process parameters:**

It should not be necessary to change these parameters. To be able to reach
actinia a correct actinia base URL (`ACTINIA_BASE_URL`) is required. The default
 of this setup is `http://localhost:8088/`.

**STAC parameters:**

- `STAC_CATALOG_URL`: Should link to the STAC catalog `"http://pycsw:8000/stac/"`
- `STAC_COLLECTIONS`: Names of the STAC collections, where the created items are
 registered.
 For this workflow four collections for each product are used:
 `"ndvi-ath,ndvi-cat-ath,ndwi-ath,ndwi-cat-ath"`
- `PRODUCT_NAMES`: Names used for the STAC items of the four products (same
order as `STAC_COLLECTIONS`): `"NDVI,NDVI_categorized,NDWI,NDWI_categorized"`
- `STAC_ITEM_ID_PREFIX`: Defines a prefix for the STAC item IDs: e.g.
`"athen_urban_green"` so the STAC item ID will be like this
`athen_urban_green_NDWI_categorized_20260218T091031`
`STAC_ITEM_TITLE`: Title for STAC item. Additionally, product name and date are
added to the title. E.g. `Urban Green Monitoring Athens- NDWI_categorized - 2026-02-18 09:10:31+00:00`
`STAC_ITEM_DESCRIPTION`: Description for STAC item. Currently it is the same
text for all products.

**Note for a local setup**: Adding STAC item to a collection only works if you
have write access to the collection.

Required python dependencies for `run_service.py` are listed in `requirements.txt`
and include:

- `requests`
- `dotenv`
- `jinja2`

## Output layers

The main output layers are exported as Cloud Optimized GeoTIFFs (COG):
- NDVI (Normalized Difference Vegetation Index)
- Categorized NDVI
- NDWI (Normalized Difference Water Index)
- Categorized NDWI

Categorization thresholds for NDVI and NDWI are defined in `processing/input/index_classification/ndvi_4_classes` and `processing/input/index_classification/ndwi_3_classes`.

Uses equations:
- NDVI = (NIR - Red) / (NIR + Red)
- NDWI = (( NIR - SWIR ) / ( NIR + SWIR ))

NDVI classes (raster values in brackets):
- no vegetation (1): -1 to 0.1
- bare soil (2): 0.1 to 0.2
- sparse/stressed vegetation (3): 0.2 to 0.5
- dense/healthy vegetation (4): 0.5 to 1.0

NDWI classes (raster values in brackets):
- barren soil (1): -1000 to -200  
- strong water stress (2): -200 to 0  
- medium water stress (3): 0 to 100  
- low water stress (4): 100 to 200  
- no water stress (5): 200 to 1000


## Troubleshooting

- Authentication failures:
  - verify `ACTINIA_USER`, `ACTINIA_PW`, `EODAG_USER`, `EODAG_PW` in
    `docker/.env`.
- No scenes returned:
  - widen time window, increase cloud threshold, verify tile ID and AOI.
- Process polling errors:
  - inspect actinia status URL and container logs for detailed module errors.

## Repository structure

```text
.
├── docker
│   └── ...
├── grass-gis-addons
│   ├── i.create.stac
│   │   └── ...
│   ├── i.s2_id.download
│   │   └── ...
│   └── i.s2_id.filter
│       └── ...
├── LICENSES
│   └── GPL-3.0-or-later.txt
├── processing
│   ├── input
│   │   ├── aoi
│   │   │   └── Athens_aoi.geojson
│   │   └── index_classification
│   │       └── ...
│   ├── run_service.py
│   ├── scripts
│   │   ├── create_export_subfolders.py
│   │   ├── remove_data.py
│   │   └── rename_bands.py
│   └── templates
│       ├── process_chain_filter_S2_scenes.json
│       ├── process_chain_filter_S2_scenes.json.j2
│       ├── process_chain_S2_processing.json
│       ├── process_chain_S2_processing.json.j2
│       ├── template_calc_NDVI.json
│       ├── template_calc_NDWI.json
│       ├── template_S2_download_import.json
│       └── template_S2_processing.json
├── README.md
├── requirements.txt
└── ...

```

## License

This project is licensed under GPL-3.0-or-later. See `LICENSE` and
`LICENSES/GPL-3.0-or-later.txt`.
