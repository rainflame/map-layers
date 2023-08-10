# Elevation data

Create TerrainRGB files from USGS DEM sources.

## Download the elevation data

Use `create_elevation_data.ipynb` to download the DEM files from USGS for a particular region defined by a bounding box. This will download `.tif` for that region to `/data/sources/`.

## Convert to tiles

To tile the dataset, you'll need GDAL installed, along with [rasterio](https://rasterio.readthedocs.io/en/latest/index.html) and [rio-rgbify](https://github.com/mapbox/rio-rgbify).

First, build a virtual dataset with GDAL:

```
gdalbuildvrt -overwrite -srcnodata -9999 -vrtnodata -9999 data/dem.vrt data/sources/*.tif
```

Then, build a `.mbtiles` file using `rio`:

```
rio rgbify -b -10000 -i 0.1 --min-z 6 --max-z 12 -j 8 --format webp data/dem.vrt data/rgb.mbtiles
```

Note that you'll want to change the number of cores in this command (`-j 8` in the example above) to an appropriate number given the computer you're running it on.

I ran into [this issue](https://github.com/mapbox/rio-rgbify/issues/39) when running `rgbify`, with the only workaround being to manually edit the source code to remove the buggy line as [done here](https://github.com/acalcutt/rio-rgbify/commit/6db4f8baf4d78e157e02c67b05afae49289f9ef1). Hopefully this gets fixed in the future, but as of the time of writing this the workaround is necessary.
