#!/bin/bash

echo -e "\nConverting to GeoJSON...\n"

ogr2ogr -f GeoJSONSeq data/temp/water.geojsons data/temp/water.gpkg
ogr2ogr -f GeoJSONSeq data/temp/waterways.geojsons data/temp/waterways.gpkg

echo -e "\nTiling dataset...\n"

tippecanoe -Z1 -z16 -P -o data/output/water.pmtiles \
           --drop-densest-as-needed \
           --simplification=5 \
           --hilbert \
           --maximum-tile-bytes=350000 \
           --visvalingam \
           -l water data/temp/water.geojsons \
           --force

tippecanoe -Z1 -z16 -P -o data/output/waterways.pmtiles \
           --drop-densest-as-needed \
           --simplification=5 \
           --hilbert \
           --maximum-tile-bytes=350000 \
           --visvalingam \
           -l waterways data/temp/waterways.geojsons \
           --force
           

echo -e "\n\nDone, created: \ndata/output/water.pmtiles\ndata/outupt/waterways.pmtiles\n"
