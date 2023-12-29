#!/bin/bash


echo "Converting to geojson..."
ogr2ogr \
    -f GeoJSONSeq \
    data/temp/peaks_prominence_1.geojsons \
    data/temp/peaks_prominence_1.gpkg \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/peaks_prominence_2.geojsons \
    data/temp/peaks_prominence_2.gpkg \
    -progress

ogr2ogr \
    -f GeoJSONSeq \
    data/temp/peaks_prominence_3.geojsons \
    data/temp/peaks_prominence_3.gpkg \
    -progress

echo "Tiling dataset..."
tippecanoe \
    -Z10 \
    -z16 \
    -l peaks_prominence_1 \
    data/temp/peaks_prominence_1.geojsons \
    --read-parallel \
    -o data/temp/peaks_prominence_1.pmtiles \
    -P \
    --force

tippecanoe \
    -Z11 \
    -z16 \
    -l peaks_prominence_2 \
    data/temp/peaks_prominence_2.geojsons \
    --read-parallel \
    -o data/temp/peaks_prominence_2.pmtiles \
    -P \
    --force

tippecanoe \
    -Z12 \
    -z16 \
    -l peaks_prominence_3 \
    data/temp/peaks_prominence_3.geojsons \
    --read-parallel \
    -o data/temp/peaks_prominence_3.pmtiles \
    -P \
    --force



echo "Combining tiles..."
tile-join -o data/output/peaks.pmtiles \
    data/temp/peaks_prominence_1.pmtiles \
    data/temp/peaks_prominence_2.pmtiles \
    data/temp/peaks_prominence_3.pmtiles \
    --force


echo -e "\n\nDone, created: \ndata/output/peaks.pmtiles\n"
