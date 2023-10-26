#!/bin/bash

echo -e "\nTiling dataset...\n"

# tile contours, creating three separate files with 40ft, 200ft, and 1000ft contours at different zoom levels
tippecanoe -Z10 -z18 -P -y elevation -l contour_1000 \
    -o data/temp/contour_1000.mbtiles \
    data/temp/1000/*.geojsons --force --read-parallel

tippecanoe -Z11 -z18 -P -y elevation -l contour_200 \
    -o data/temp/contour_200.mbtiles \
    data/temp/200/*.geojsons --force --read-parallel

tippecanoe -Z12 -z18 -P -y elevation -l contour_40 \
    -o data/temp/contour_40.mbtiles \
    data/temp/40/*.geojsons --force --read-parallel

echo -e "\nMerging layers...\n"

tile-join -o data/output/contours.mbtiles data/temp/contour_1000.mbtiles data/temp/contour_200.mbtiles data/temp/contour_40.mbtiles --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/output/contours.mbtiles data/output/contours.pmtiles

echo -e "\nDone, created:\ndata/output/contours.mbtiles\ndata/output/contours.pmtiles\n"
