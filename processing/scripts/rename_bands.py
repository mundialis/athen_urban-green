#!/usr/bin/env python3
# ruff: noqa: D100
############################################################################
# MODULE:      rename_bands
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Rename bands in process chain for handling S2 scenes
#
# SPDX-FileCopyrightText: (c) 2025 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################

import grass.script as grass


def main() -> None:
    """Rename bands in process chain for handling S2 scenes."""
    print(grass.parse_command("g.list", type="raster", mapset="."))
    for band in list(
        grass.parse_command("g.list", type="raster", pattern="T*", mapset=".")
    ):
        new_name = f"{band.split('_')[2]}"
        grass.run_command(
            "g.rename",
            raster=f"{band},{new_name}",
            overwrite=True,
        )


if __name__ == "__main__":
    main()
