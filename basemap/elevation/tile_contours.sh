#!/bin/bash

echo -e "\nTiling dataset...\n"

# assuming $1 is 40 ft contours, $2 is 200 ft contours, $3 is 1000 ft contours and $4 is the output file
if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ]; then
    echo "Usage: $0 <40ft_contours> <200ft_contours> <1000ft_contours> <output file>"
    exit 1
fi

# tile contours, creating three separate files with 40ft, 200ft, and 1000ft contours at different zoom levels
tippecanoe \
    -Z12 \
    -z16 \
    -y elevation \
    -l contour_40 \
    "$1" \
    --read-parallel \
    --drop-densest-as-needed \
    --simplification=5 \
    --hilbert \
    --visvalingam \
    -o data/temp/contour_40.pmtiles \
    -P \
    --force

tippecanoe \
    -Z11 \
    -z16 \
    -y elevation \
    -l contour_200 \
    "$2" \
    --read-parallel \
    --drop-densest-as-needed \
    --simplification=5 \
    --hilbert \
    --visvalingam \
    -o data/temp/contour_200.pmtiles \
    -P \
    --force

tippecanoe \
    -Z10 \
    -z16 \
    -y elevation \
    -l contour_1000 \
    "$3" \
    --read-parallel \
    --drop-densest-as-needed \
    --simplification=5 \
    --hilbert \
    --visvalingam \
    -o data/temp/contour_1000.pmtiles \
    -P \
    --force

echo -e "\nMerging layers...\n"

tile-join \
    -o "$4" \
    data/temp/contour_1000.pmtiles \
    data/temp/contour_200.pmtiles \
    data/temp/contour_40.pmtiles --force

echo -e "\n\nDone, created:\n$4\n"
