#!/bin/bash

mkdir -p data/output

echo "Converting to geojson..."
ogr2ogr \
    -f GeoJSONSeq \
    data/temp/place-polygons.geojsons \
    data/temp/place-polygons.gpkg \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/place-points.geojsons \
    data/temp/place-points.gpkg \
    -progress


echo -e "\nTiling dataset...\n"

tippecanoe \
    -Z1 \
    -z16 \
    -o data/temp/place-polygons.pmtiles \
    -l boundaries \
    --drop-densest-as-needed \
    --read-parallel \
    data/temp/place-polygons.geojsons \
    -P \
    --force

tippecanoe \
    -Z1 \
    -z16 \
    -o data/temp/place-points.pmtiles \
    -l places \
    --drop-densest-as-needed \
    --read-parallel \
    data/temp/place-points.geojsons \
    -P \
    --force

echo -e "\nCombining place points and polygons...\n"

tile-join \
    -o data/output/places.pmtiles \
    data/temp/place-polygons.pmtiles \
    data/temp/place-points.pmtiles --force

echo -e "\n\nDone, created: \ndata/output/places.pmtiles\n"
