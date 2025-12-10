#!/usr/bin/env python3

import os
import shutil
import sys


def main():
    folder_path = sys.argv[1]

    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)
        else:
            shutil.rmtree(item_path)

if __name__ == "__main__":
    main()