#!/bin/bash

# assuming $1 is the input file and $2 is the output file
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <input_file> <output_file>"
    exit 1
fi

echo "SNOW PIPELINE/TILING: Converting to GeoJSON..."

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/snow-contours.geojsons \
   "$1"

echo "SNOW PIPELINE/TILING: Creating tiles..."

tippecanoe -Z1 -z16 -P \
         --drop-densest-as-needed \
         -l snow data/temp/snow-contours.geojsons \
         -o "$2" \
          --force

echo "SNOW PIPELINE/TILING: Done, created $2"
