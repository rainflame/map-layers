#!/bin/bash

echo -e "\nTiling dataset...\n"

# tile contours, creating layers elevation_1000 from 10-11, elevation_200 from 11-12, and elevation_40 from 12+
# see https://github.com/nst-guide/terrain/blob/4671546d2a17b1ed4e71a2e1648e5ffc595c3217/README.md?plain=1#L452-L468
tippecanoe -Z10 -z20 -P -y elevation -l contour_1000 \
    -C 'jq "if .properties.elevation % 1000 == 0 then . else {} end"' \
    -o data/contour_1000.mbtiles \
    data/temp/*.geojson --force

tippecanoe -Z11 -z20 -P -y elevation -l contour_200 \
    -C 'jq "if .properties.elevation % 200 == 0 then . else {} end"' \
    -o data/contour_200.mbtiles \
    data/temp/*.geojson --force

tippecanoe -Z12 -z20 -P -y elevation -l contour_40 \
    -C 'jq "if .properties.elevation % 40 == 0 then . else {} end"' \
    -o data/contour_40.mbtiles \
    data/temp/*.geojson --force

echo -e "\nMerging layers...\n"

tile-join -o data/contours.mbtiles data/contour_1000.mbtiles data/contour_200.mbtiles data/contour_40.mbtiles --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/contours.mbtiles data/contours.pmtiles

echo -e "\nDone, created contours.pmtiles\n"
