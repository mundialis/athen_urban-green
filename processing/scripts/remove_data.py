#!/usr/bin/env python3
# ruff: noqa: D100, PTH118, PTH208
############################################################################
# MODULE:      remove_data
# AUTHOR(S):   Jonas Pischke
#
# PURPOSE:     Remove downloaded S2 scenes
#
# SPDX-FileCopyrightText: (c) 2025 by mundialis GmbH & Co. KG
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
############################################################################
import os
import shutil
import sys


def main() -> None:
    """Clean up function for removing downloaded files in a specific folder.

    Returns:
            None

    """
    folder_path = sys.argv[1]

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        shutil.rmtree(item_path)


if __name__ == "__main__":
    main()
