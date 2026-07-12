## Description

*i.s2_id.filter* Filter S2 scenes via given search parameter using
eodag. With **-a** flag the current region is used as AOI for filtering
S2 scenes (overrides lonmin, lonmax, latmin, latmax options).

## EXAMPLES

```sh
i.s2_id.filter start_time="2021-01-01" end_time="2021-01-31" cloud_coverage=80 tile_id="32TQM" -a \
```

## SEE ALSO

See also:  

- [EODAG
  library](https://eodag.readthedocs.io/en/stable/getting_started_guide/install.html)

## AUTHORS

Jonas Pischke, [mundialis GmbH & Co. KG](https://www.mundialis.de/),
Germany
