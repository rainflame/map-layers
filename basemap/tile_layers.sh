layers=(
    # "elevation/data/output/contours.mbtiles"
    "glaciers/data/output/glaciers.mbtiles"
    "glaciers/data/output/glacier_labels.mbtiles"
)

# filter out any files in the layers array that don't exist
layers=($(for i in "${layers[@]}"; do if [ -f "$i" ]; then echo $i; fi; done))

printf "\nCombining layers:\n\n"
printf '%s\n' "${layers[@]}"
printf "\n"

tile-join -o data/output/basemap.mbtiles ${layers[@]} --force