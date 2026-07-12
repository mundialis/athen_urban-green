# Description

*i.s2_id.filter* Filter S2 scenes via given search parameter using the
EODAG library. With **-a** flag the current region is used as AOI for
filtering S2 scenes (overrides lonmin, lonmax, latmin, latmax options).

## EXAMPLES

```sh
i.s2_id.filter start_time="2021-01-01" end_time="2021-01-31" cloud_coverage=80 tile_id="32TQM" -a
```

## REQUIREMENTS

- [EODAG
  library](https://eodag.readthedocs.io/en/stable/getting_started_guide/install.html)
  (install with `pip install eodag`)
- For EODAG 3.0.0 and later, some of the providers have additonal
  dependencies that needs to be installed, e.g.
  `pip install eodag[usgs]`, for more info see [installation
  page](https://eodag.readthedocs.io/en/stable/getting_started_guide/install.html).
  To install all dependencies use `pip install eodag[all]`

## SEE ALSO

*[i.sentinel](i.sentinel.md)*

## AUTHORS

Jonas Pischke, [mundialis GmbH & Co. KG](https://www.mundialis.de/),
Germany
