#!/bin/bash

set -e 

echo "CONTOUR PIPELINE: Creating contours from DEMs..."

python create_contours.py \
    --input-files="data/sources/*.tif"

echo "CONTOUR PIPELINE: Filtering overlapping contours..."

ogr2ogr \
    -f "GPKG" \
    -sql "SELECT * FROM \"elevation\" WHERE elevation % 1000 != 0" \
    "data/temp/contour_200_filtered.gpkg" \
    "data/temp/contour_200.gpkg" 

ogr2ogr \
    -f "GPKG" \
    -sql "SELECT * FROM \"elevation\" WHERE elevation % 1000 != 0" \
    "data/temp/contour_40_filtered.gpkg" \
    "data/temp/contour_40.gpkg" 

echo "CONTOUR PIPELINE: Tiling contours..."

bash tile_contours.sh \
    data/temp/contour_40_filtered.gpkg \
    contour_40_landcover \
    data/temp/contour_200_filtered.gpkg \
    contour_200_landcover \
    data/temp/contour_1000.gpkg \
    contour_1000_landcover \
    data/output/contours.pmtiles

echo "CONTOUR PIPELINE: Done."