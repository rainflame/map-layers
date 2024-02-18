#!/bin/bash

echo -e "\nTiling dataset...\n"

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ] || [ -z "$4" ] || [ -z "$5" ] || [ -z "$6" ] || [ -z "$7" ]; then
    echo -e "Usage: $0 <40ft_contours> <40ft_contour_label> <200ft_contours> <200ft_contour_label> <1000ft_contours> <1000ft_contour_label> <output file>"
    exit 1
fi

# convert each input file to geojsonseq
echo "CONTOUR PIPELINE/TILING: Converting to geojsonseq..."
ogr2ogr \
    -f GeoJSONSeq \
    data/temp/contour_40.geojsons \
    "$1" \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/contour_200.geojsons \
    "$3" \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/contour_1000.geojsons \
    "$5" \
    -progress


echo "CONTOUR PIPELINE/TILING: Creating tiles..."
# tile contours, creating three separate files with 40ft, 200ft, and 1000ft contours at different zoom levels
tippecanoe \
    -Z12 \
    -z16 \
    -y elevation \
    -l "${2}" \
    data/temp/contour_40.geojsons \
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
    -l "${4}" \
    data/temp/contour_200.geojsons \
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
    -l "${6}" \
    data/temp/contour_1000.geojsons \
    --read-parallel \
    --drop-densest-as-needed \
    --simplification=5 \
    --hilbert \
    --visvalingam \
    -o data/temp/contour_1000.pmtiles \
    -P \
    --force

echo "CONTOUR PIPELINE/TILING: Joining tiles..."
tile-join \
    -o "$7" \
    data/temp/contour_1000.pmtiles \
    data/temp/contour_200.pmtiles \
    data/temp/contour_40.pmtiles --force

echo "CONTOUR PIPELINE/TILING: Done, created $7"