#!/bin/bash

echo -e "\nConverting to GeoJSON...\n"

ogr2ogr -f GeoJSONSeq data/temp/snow-contours.geojsons data/temp/snow-contours.gpkg

echo -e "\nTiling dataset...\n"

tippecanoe -Z1 -z16 -P \
         --drop-densest-as-needed \
         -l snow data/temp/snow-contours.geojsons \
         -o data/output/snow.pmtiles \
          --force

echo -e "\n\nDone, created: \ndata/output/snow.pmtiles\n"
