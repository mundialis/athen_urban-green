# Urban Green Monitoring for the Municipality of Athens

This repository contains the processing stack used to monitor urban green areas
in Athens from Earth Observation data (Sentinel-2). It combines:

- an actinia + GRASS GIS processing backend,
- custom GRASS add-ons for Sentinel-2 scene filtering, Sentinel-2 scene download and STAC publishing,
- process chain templates for NDVI/NDWI production and classification.

The main output is a set of geospatial products (NDVI/NDWI and classified
versions) plus STAC item updates for catalog publication.

**Note**: This workflow was designed to be integrated with the [satellite.cityofathens.gr](https://github.com/EOFarm/satellite.cityofathens.gr) repository. Adding STAC items of processed raster layers to STAC collection might not work properly if running this worklow independently (needs correct STAC catalog setup).

## What this workflow does

The workflow in this repository is designed to:

1. Filter Sentinel-2 scenes by date range, AOI, tile id, and cloud cover.
2. Download and import selected scenes into GRASS GIS.
3. Compute NDVI and NDWI maps.
4. Classify NDVI/NDWI outputs using configured categories for vegetation health assessment.
5. Export raster outputs as COG.
6. Create and publish STAC items to an existing STAC catalog/collection and update collection extent metadata.

## Main components 

#### Custom GRASS Addons

In `./grass-gis-addons/`

- `i.s2_id.filter`
    - Module to query Sentinel-2 metadata via `EODAG` and return scene IDs based on filters (date, AOI, tile id, cloud cover).
- `i.s2_id.download`
    - Module to download selected Sentinel-2 scenes using `EODAG`. Imports bands using `i.sentinel.import` for processing.
- `i.create.stac`
    - Module to create a STAC item from exported assets and publish it to an existing STAC catalog/collection. Also updates collection extents. Uses `pystac` and `rio-stac`.

#### Scripts

In `./processing/scripts/`

- create_export_subfolders.py
    - utility script to create export directory for exported COGs. Directory is parsed in process chain template.
- remove_data.py
    - cleanup script to remove downloaded Sentinel-2 SAFE files.
- rename_bands.py
    - utility script to rename imported raster bands in GRASS location for further processing.

#### Actinia Process Chains 

Jinja2 templates in `./processing/templates/`. Variables are parsed in `run_service.py` and rendered as JSON before submission to actinia.

- `process_chain_filter_S2_scenes.json.j2`
    - process chain to run `i.s2_id.filter` and return filtered scene ids.
- `process_chain_S2_processing.json.j2`
    - process chain to trigger processing for parsed Sentinel-2 scene ids. 

#### Actinia Process Templates

Actinia module templates in `./processing/templates/` are used by `process_chain_S2_processing.json.j2`.

- `template_S2_processing.json` 
    - process template to run the main processing steps for a Sentinel-2 scene: import, NDVI/NDWI calculation, classification, export, and STAC item creation. Calls the following templates for specific steps:
    - `template_S2_download_import.json`
        - process template to download Sentinel-2 scenes using `i.s2_id.download` and to import bands using `i.sentinel.import`.
    - `template_calc_NDVI.json`
        - process template to calculate NDVI and categorize it. Exports layers as COG.
    - `template_calc_NDWI.json`
        - process template to calculate NDWI and categorize it. Exports layers as COG.

#### Start service script
- `processing/run_service.py`
    - script to run the whole workflow. Parses parameters, renders process chain templates, submits to actinia, and monitors execution.


## How to use this workflow

All Docker commands below are run from the `docker/` directory. For further docker instructions see `docker/README.md`.

### 1. Configure environment variables

Create `docker/.env` with actinia and [CDSE](https://dataspace.copernicus.eu/) credentials:

```env
ACTINIA_USER=<your_user>
ACTINIA_PW=<your_password>
EODAG_USER=<your_CDSE_user>
EODAG_PW=<your_CDSE_password>
```

***Do not commit real credentials in `docker/.env`.***

### 2. Build the image

```bash
docker compose -f docker-compose.yml -p athen_urban-green build
```

For a full rebuild after dependency changes:

```bash
docker compose -f docker-compose.yml -p athen_urban-green build --no-cache
```

### 3. Start containers

For a **Local Setup:** you need to mount a local directory for data export. Add to volumes fo actinia `/path/to/local/export/dir:/src/export_dir`

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

## Running processing

### Run Service

The script in `processing/run_service.py` starts the whole workflow. 

From repository root:

```bash
python processing/run_service.py
```

Important script parameters to adapt before production runs:

- Time range (`START_TIME`, `END_TIME`, or automatic time range mode) for filtering Sentinel-2 scenes. Options: 
    - autmatic time range mode: Queries given STAC collection for latest item and sets `START_TIME` accordingly and `END_TIME` to current time.
- AOI: By default, the script uses a predefined AOI for Athens in `processing/input/athens_aoi.geojson`. 
    - To use a different AOI, replace this file with a new GeoJSON containing the desired AOI geometry (and rebuild image).
    - Or specify a bound box by setting `LONMIN`, `LONMAX`, `LATMIN`, `LATMAX`. 
        - **ToDo**: Currently -a flag is set for i.s2_id.filter in process chain. This enables AOI filtering based on predifines AOI. For bounding box filtering -a flag must be removed. --> implement automatic flag removal when bounding box parameters are set.
- `TILE_ID`: Sentinel-2 tile identifier e.g. `34SGH` for Athens area
- Max. cloud cover threshold (`MAX_CLOUD_COVER`)
- Actinia base URL, processing endpoint and GRASS location settings
- STAC catalog URL and collection names
- STAC item metadata settings (e.g. collection extent update, item asset metadata)

**Note for a local setup**: Adding STAC item to a collection only works if you have write access to the collection. 

Required python depencies for `run_service.py`:
- requests
- dotenv
- jinja2

## Troubleshooting

- Authentication failures:
	- verify `ACTINIA_USER`, `ACTINIA_PW`, `EODAG_USER`, `EODAG_PW` in `docker/.env`.
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
└── ...

```

## License

This project is licensed under GPL-3.0-or-later. See `LICENSE` and
`LICENSES/GPL-3.0-or-later.txt`.
