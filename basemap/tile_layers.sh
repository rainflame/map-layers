layers=(
    "elevation/data/output/contours.mbtiles"
    "glaciers/data/output/glaciers.mbtiles"
)

# filter out any files in the layers array that don't exist
layers=($(for i in "${layers[@]}"; do if [ -f "$i" ]; then echo $i; fi; done))

printf "\nFound layers to combine:\n\n"
printf '%s\n' "${layers[@]}"
printf "\n"

echo -e "\nCombining layers...\n"

tile-join -o data/output/basemap.mbtiles ${layers[@]} --force

echo -e "\nConverting to pmtiles format...\n"

pmtiles convert data/output/basemap.mbtiles data/output/basemap.pmtiles

echo -e "\nDone, created: \ndata/output/basemap.mbtiles\ndata/output/basemap.pmtiles\n"