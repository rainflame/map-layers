#!/bin/bash

mkdir -p data/output

echo -e "\nTiling dataset...\n"

# tile glacier text lines 
tippecanoe -Z1 -z16 -P -o data/output/glacier_labels.mbtiles --drop-densest-as-needed -l glacier-labels data/temp/axes.geojson --force

# tile glacier polygons 
tippecanoe -Z1 -z16 -P -o data/output/glaciers.mbtiles --drop-densest-as-needed -l glaciers data/temp/glaciers.geojson --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/output/glaciers.mbtiles data/output/glaciers.pmtiles
pmtiles convert data/output/glacier_labels.mbtiles data/output/glacier_labels.pmtiles

echo -e "\nDone, created: \ndata/output/glaciers.mbtiles\ndata/output/glaciers.pmtiles\ndata/output/glacier_labels.mbtiles\ndata/output/glacier_labels.pmtiles\n"
