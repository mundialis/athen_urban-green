#!/usr/bin/env python3
# ruff: noqa: D100
############################################################################
# MODULE:      create_export_subfolders
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Create subfolders for export data
#
# SPDX-FileCopyrightText: (c) 2026 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################
import sys
from pathlib import Path


def main() -> None:
    """Create subfolders for export data.

    Returns:
            None

    """
    folder_path = sys.argv[1]

    # check if the directory exists
    if not Path(folder_path).exists():
        # create the directory
        Path(folder_path).mkdir(parents=True)
        print(f"Directory '{folder_path}' created.")
    else:
        print(f"Directory '{folder_path}' already exists.")


if __name__ == "__main__":
    main()
