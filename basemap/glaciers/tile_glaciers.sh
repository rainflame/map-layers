#!/bin/bash

mkdir -p data/output

echo "Converting to geojson..."
ogr2ogr \
    -f GeoJSONSeq \
    data/temp/glaciers.geojsons \
    data/temp/glaciers.gpkg \
    -progress

echo -e "\nTiling dataset...\n"
# tile glacier text lines 
# tippecanoe -Z1 -z16 -P -o data/temp/glacier_labels.pmtiles --drop-densest-as-needed -l glacier-labels data/temp/glacier-labels.geojson --force

# tile glacier polygons 
tippecanoe \
    -Z1 \
    -z16 \
    -o data/output/glaciers.pmtiles \
    -l glaciers \
    --drop-densest-as-needed \
    --read-parallel \
    data/temp/glaciers.geojsons \
    -P \
    --force

# echo -e "\nCombining glacier polygons and text labels...\n"

# tile-join -o data/output/glaciers.pmtiles data/temp/glacier_labels.pmtiles data/temp/glaciers_outlines.pmtiles --force


echo -e "\n\nDone, created: \ndata/output/glaciers.pmtiles\n"
