#!/bin/bash

mkdir -p data/output

echo "Converting to geojson..."
ogr2ogr \
    -f GeoJSONSeq \
    data/temp/glaciers.geojsons \
    data/temp/glaciers.gpkg \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/glaciers-labels.geojsons \
    data/temp/glaciers-labels.gpkg \
    -progress


echo -e "\nTiling dataset...\n"

tippecanoe \
    -Z1 \
    -z16 \
    -o data/temp/glaciers.pmtiles \
    -l glaciers \
    --drop-densest-as-needed \
    --read-parallel \
    data/temp/glaciers.geojsons \
    -P \
    --force

tippecanoe \
    -Z1 \
    -z16 \
    -o data/temp/glaciers-labels.pmtiles \
    -l glacier-labels \
    --drop-densest-as-needed \
    --read-parallel \
    data/temp/glaciers-labels.geojsons \
    -P \
    --force

echo -e "\nCombining glacier polygons and text labels...\n"

tile-join \
    -o data/output/glaciers.pmtiles \
    data/temp/glaciers-labels.pmtiles \
    data/temp/glaciers.pmtiles --force

echo -e "\n\nDone, created: \ndata/output/glaciers.pmtiles\n"
