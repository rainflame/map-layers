#!/bin/bash

cd data

echo -e "\nTiling dataset...\n"

ogr2ogr -f GeoJSON -t_srs crs:84 fires.geojson fires.shp

tippecanoe -zg -o fires.mbtiles -l fire --drop-densest-as-needed fires.geojson --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert fires.mbtiles fires.pmtiles

echo -e "\nCleaning up...\n"

rm fires.mbtiles
rm fires.geojson

echo -e "\nDone, created fires.pmtiles\n"