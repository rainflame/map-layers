#!/bin/bash

mkdir -p data/output

echo -e "\nTiling dataset...\n"

tippecanoe -zg -o data/output/glaciers.mbtiles --drop-densest-as-needed -l glaciers data/temp/glaciers.geojson --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/output/glaciers.mbtiles data/output/glaciers.pmtiles

echo -e "\nDone, created: \ndata/output/glaciers.mbtiles\ndata/output/glaciers.pmtiles\n"
