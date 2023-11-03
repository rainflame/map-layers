#!/bin/bash

mkdir -p data/output

echo -e "\nTiling dataset...\n"

# tile glacier text lines 
tippecanoe -Z1 -z16 -P -o data/temp/glacier_labels.mbtiles --drop-densest-as-needed -l glacier-labels data/temp/glacier-labels.geojson --force

# tile glacier polygons 
tippecanoe -Z1 -z16 -P -o data/temp/glaciers_outlines.mbtiles --drop-densest-as-needed -l glaciers data/temp/glaciers-cleaned.geojson --force

echo -e "\nCombining glacier polygons and text labels...\n"

tile-join -o data/output/glaciers.mbtiles data/temp/glacier_labels.mbtiles data/temp/glaciers_outlines.mbtiles --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/output/glaciers.mbtiles data/output/glaciers.pmtiles

echo -e "\nDone, created: \ndata/output/glaciers.mbtiles\ndata/output/glaciers.pmtiles\n"
