#!/usr/bin/env python3

import atexit
import grass.script as grass

def cleanup():
    pass

def main():
    print(grass.parse_command('g.list', type='raster', mapset='.'))
    for band in list(grass.parse_command('g.list', type='raster', mapset='.')):
        new_name = f"{band.split('_')[2]}"
        grass.run_command('g.rename',
                        raster=f'{band},{new_name}',
                        overwrite=True)

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
