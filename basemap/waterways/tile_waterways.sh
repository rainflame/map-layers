#!/bin/bash

echo "Converting to GeoJSON..."

ogr2ogr -f GeoJSONSeq data/temp/water.geojsons data/temp/water.gpkg
ogr2ogr -f GeoJSONSeq data/temp/waterways.geojsons data/temp/waterways.gpkg
ogr2ogr -f GeoJSONSeq data/temp/water-labels.geojsons data/temp/water-labels.gpkg

echo "Tiling dataset..."

tippecanoe -Z11 -z16 -P \
           -o data/temp/water-labels.pmtiles \
           --drop-densest-as-needed \
           -l water-labels \
           data/temp/water-labels.geojsons \
           --force

tippecanoe -Z1 -z16 -P \
            -o data/temp/water.pmtiles \
           --drop-densest-as-needed \
           --simplification=5 \
           --hilbert \
           --maximum-tile-bytes=350000 \
           --visvalingam \
           -l water \
           data/temp/water.geojsons \
           --force

tippecanoe -Z1 -z16 -P \
            -o data/temp/waterways.pmtiles \
           --drop-densest-as-needed \
           --simplification=5 \
           --hilbert \
           --maximum-tile-bytes=350000 \
           --visvalingam \
           -l waterways \
           data/temp/waterways.geojsons \
           --force

echo "Combining layers..."  

tile-join -o data/output/water.pmtiles \
          data/temp/waterways.pmtiles \
          data/temp/water.pmtiles \
          data/temp/water-labels.pmtiles  \
          --force


echo -e "\n\nDone, created: \ndata/output/water.pmtiles"
