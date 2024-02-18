#!/bin/bash

set -e 

# assuming $1 is the bounding box
if [ -z "$1" ]; then
    echo "Usage: $0 <bounding_box>"
    exit 1
fi

echo "SNOW PIPELINE: Quantizing raster..."

python quantize.py \
    --input-file="data/sources/snow-conus.tif" \
    --output-file="data/temp/snow-quantized.tif" \
    --bin-size=12 \
    --bbox="$1" 

echo "SNOW PIPELINE: Polygonizing raster..."

geopolygonize \
    --input-file="data/temp/snow-quantized.tif" \
    --output-file="data/temp/snow-contours.gpkg" \
    --simplification-pixel-window=1 \
    --min-blob-size=12 \
    --smoothing-iterations=1 \
    --label-name="depth"

echo "SNOW PIPELINE: Cleaning polygons..."

ogr2ogr \
    -f GPKG \
    data/temp/snow-final.gpkg \
    data/temp/snow-contours.gpkg \
    -nln snow \
    -where "depth != 0"

echo "SNOW PIPELINE: Tiling..."

./tile_snow.sh \
    data/temp/snow-final.gpkg \
    data/output/snow.pmtiles

echo "SNOW PIPELINE: Done."