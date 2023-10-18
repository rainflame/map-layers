import rasterio 
import glob
import os 
import shutil

import numpy as np
from tqdm import tqdm


if not os.path.exists("data/temp"):
    os.makedirs("data/temp")
else:
    # delete the existing files and make it again
    shutil.rmtree("data/temp")
    os.makedirs("data/temp")

# get the tif file from data/landfire_vegetation
file = glob.glob('data/sources/*.tif')[0]

print("Splitting raster bands into individual files...")

with rasterio.open(file) as src:

    meta = src.meta
    meta.update(dtype='uint8')
    meta.update(nodata=0)

    band1 = src.read(1)
    band1_unique = np.unique(band1)

    for value in tqdm(band1_unique):
        band1 = src.read(1)
        # set everything that's not this value to 0
        band1[band1 != value] = 0
        band1[band1 == value] = 255

        # save this band as a new rgba image
        with rasterio.open("data/temp/{}.tif".format(int(value)), 'w', **meta) as dst:
            dst.write_band(1, band1)

print("Done!")
