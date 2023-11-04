#!/bin/bash

echo -e "\nTiling dataset...\n"

# tile contours, creating three separate files with 40ft, 200ft, and 1000ft contours at different zoom levels
tippecanoe -Z10 -z16 -P -y elevation -l contour_1000 \
    -o data/temp/contour_1000.pmtiles \
    data/temp/1000/*.geojsons --force --read-parallel

tippecanoe -Z11 -z16 -P -y elevation -l contour_200 \
    -o data/temp/contour_200.pmtiles \
    data/temp/200/*.geojsons --force --read-parallel

tippecanoe -Z12 -z16 -P -y elevation -l contour_40 \
    -o data/temp/contour_40.pmtiles \
    data/temp/40/*.geojsons --force --read-parallel

echo -e "\nMerging layers...\n"

tile-join -o data/output/contours.pmtiles data/temp/contour_1000.pmtiles data/temp/contour_200.pmtiles data/temp/contour_40.pmtiles --force

echo -e "\n\nDone, created:\ndata/output/contours.pmtiles\n"
