#!/bin/bash

echo -e "\nConverting to GeoJSON...\n"

ogr2ogr -f GeoJSONSeq data/temp/wildfires.geojsons data/temp/wildfires-dedupped.gpkg

echo -e "\nTiling dataset...\n"

tippecanoe -Z1 -z16 -P -o data/output/wildfires.pmtiles \
           --drop-densest-as-needed \
           --simplification=5 \
           --hilbert \
           --maximum-tile-bytes=350000 \
           --visvalingam \
           -l wildfires-historic data/temp/wildfires.geojsons \
           --force

echo -e "\n\nDone, created: \ndata/output/wildfires.pmtiles\n"
