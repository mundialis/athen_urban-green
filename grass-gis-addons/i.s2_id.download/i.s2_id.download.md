# Description

*i.s2_id.download* Downloads S2 scene from Copernicus Data Space by
given ID using the EODAG library.

## EXAMPLES

```sh
i.s2_id.download s2_id=S2B_MSIL2A_20240109T103329_N0510_R108_T32ULB_20240109T114910 \
    download_dir=/src/download_dir/ \
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
