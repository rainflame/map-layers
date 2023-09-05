#!/bin/bash

echo -e "\nTiling dataset...\n"

# tile contours, keeping the elevation property and saving to a new layer contour_40ft. Filter the contours based on the zoom levels 
# see https://github.com/nst-guide/terrain/blob/4671546d2a17b1ed4e71a2e1648e5ffc595c3217/README.md?plain=1#L452-L468
tippecanoe -Z11 -z13 -P -y elevation -l contour_40ft \
    -C 'if [ $1 -le 11 ]; then jq "if .properties.elevation % 200 == 0 then . else {} end"; elif [ $1 -eq 12 ]; then jq "if .properties.elevation % 80 == 0 then . else {} end"; else jq "."; fi' \
    -o data/contour_40ft.mbtiles \
    data/temp/*.geojson

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/contour_40ft.mbtiles data/contour_40ft.pmtiles

echo -e "\nCleaning up...\n"

rm -rf data/temp

echo -e "\nDone, created contour_40ft.pmtiles\n"
