#!/bin/bash

echo -e "\nTiling dataset...\n"

# see https://github.com/nst-guide/terrain/blob/4671546d2a17b1ed4e71a2e1648e5ffc595c3217/README.md?plain=1#L452-L468
tippecanoe -Z10 -z14 -P -y elevation -l contour_1000 \
    -C 'jq "if .properties.elevation % 1000 == 0 then . else {} end"' \
    -o data/temp/contour_1000.mbtiles \
    data/temp/*.geojson --force

tippecanoe -Z11 -z14 -P -y elevation -l contour_200 \
    -C 'jq "if .properties.elevation % 200 == 0 then . else {} end"' \
    -o data/temp/contour_200.mbtiles \
    data/temp/*.geojson --force

tippecanoe -Z12 -z14 -P -y elevation -l contour_40 \
    -C 'jq "if .properties.elevation % 40 == 0 then . else {} end"' \
    -o data/temp/contour_40.mbtiles \
    data/temp/*.geojson --force

echo -e "\nMerging layers...\n"

tile-join -o data/output/contours.mbtiles data/temp/contour_1000.mbtiles data/temp/contour_200.mbtiles data/temp/contour_40.mbtiles --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/output/contours.mbtiles data/output/contours.pmtiles

echo -e "\nDone, created:\ndata/output/contours.mbtiles\ndata/output/contours.pmtiles\n"
