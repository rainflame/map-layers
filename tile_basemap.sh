#!/bin/bash

layers=(
    "basemap/elevation/data/output/contours.pmtiles"
    # "glaciers/data/output/glaciers.pmtiles"
    # "landcover/data/output/landcover.pmtiles"
    "basemap/wildfires/data/output/wildfires.pmtiles"
    "basemap/waterways/data/output/water.pmtiles"
    "basemap/waterways/data/output/waterways.pmtiles"
)

# filter out any files in the layers array that don't exist
layers=($(for i in "${layers[@]}"; do if [ -f "$i" ]; then echo $i; fi; done))

printf "\nFound layers to combine:\n\n"
printf '%s\n' "${layers[@]}"
printf "\n"

echo -e "\nCombining layers...\n"

tile-join -o data/output/basemap.pmtiles "${layers[@]}" --force

echo -e "\n\nDone, created: \ndata/output/basemap.pmtiles\n"