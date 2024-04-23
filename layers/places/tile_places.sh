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
    data/temp/place-points-prominence-1.geojsons \
    data/temp/place-points-prominence-1.gpkg \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/place-points-prominence-2.geojsons \
    data/temp/place-points-prominence-2.gpkg \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/place-points-prominence-3.geojsons \
    data/temp/place-points-prominence-3.gpkg \
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
    -r1 \
    --no-feature-limit \
    --no-tile-size-limit \
    -o data/temp/place-points-prominence-1.pmtiles \
    -l places_p1 \
    --read-parallel \
    data/temp/place-points-prominence-1.geojsons \
    -P \
    --force

tippecanoe \
    -Z1 \
    -z16 \
    -r1 \
    --no-feature-limit \
    --no-tile-size-limit \
    -o data/temp/place-points-prominence-2.pmtiles \
    -l places_p2 \
    --read-parallel \
    data/temp/place-points-prominence-2.geojsons \
    -P \
    --force

tippecanoe \
    -Z11 \
    -z16 \
    -r1 \
    --no-feature-limit \
    --no-tile-size-limit \
    -o data/temp/place-points-prominence-3.pmtiles \
    -l places_p3 \
    --read-parallel \
    data/temp/place-points-prominence-3.geojsons \
    -P \
    --force

echo -e "\nCombining place points and polygons...\n"

tile-join \
    -o data/output/places.pmtiles \
    data/temp/place-polygons.pmtiles \
    data/temp/place-points-prominence-1.pmtiles \
    data/temp/place-points-prominence-2.pmtiles \
    data/temp/place-points-prominence-3.pmtiles \
    --force

echo -e "\n\nDone, created: \ndata/output/places.pmtiles\n"
