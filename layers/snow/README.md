# Snow

This layer represents an estimate of the current snow depth. Data is sourced from [SNODAS](https://nsidc.org/data/g02158/versions/1), a dataset for the continental United States that's updated daily.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

This script will download the latest snowcover data and transform it into GeoTIFF format:

```
./download_snow.sh
```

When complete you should have the latest snowcover data at `data/sources/snow-conus.tif` and metadata at `data/output/snow-meta.json`.

## Quantize

Next, we quantize the data to produce cleaner contours. This process converts each value of the input data into its nearest bucket. For example, assuming a bucket size of 6 inches (specified with `--bucket-size` in the script below), the value 4.3 would get bucketed into 6, the value 10.9 to 12, and so on.

We can also provide a bounding box with `--bbox` to crop the dataset to a smaller region.

```
python quantize.py --bin-size=6 --bbox="-122.04976264563147,43.51921441989123,-120.94591116755655,44.39466349563759"
```

Now you should have the quantized version of the snow raster at `data/temp/snow-quantized.tif`.

## Polygonize

Now we can convert the quantized raster into polygons with [geopolygonize](https://github.com/rainflame/geopolygonize/):

```
geopolygonize --input-file="data/temp/snow-quantized.tif" --output-file="data/temp/snow-contours.shp"
```

## Tile

Finally, create the tiled `pmtiles` archive:

```
./tile_snow.sh
```
