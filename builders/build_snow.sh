#!/bin/bash

echo -e "--- BUILDING SNOW DATASET AT [$(date +'%Y-%m-%d %H:%M:%S')] ---\n"

# get the grandparent directory of this script (prob something like /usr/local/pika-datasets)
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && cd .. && pwd )"

# get the regions we need to build files for 
if [ -f "$BASE_DIR/builders/regions.txt" ]; then
    regions=() 
    while IFS= read -r region
    do
        IFS=':' read -ra region_array <<< "$region"
        regions+=( "${region_array[@]}" )
    done < "$BASE_DIR/builders/regions.txt"
else
    echo "Build regions not found: $BASE_DIR/builders/regions.txt"
fi

# assumes we've already set up conda/mamba and created the conda environment
source "${HOME}/conda/etc/profile.d/conda.sh"
conda activate pika-datasets

cd "$BASE_DIR"/layers/snow || exit 1

mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/

# download current snow data for the entire conus
bash download_snow.sh

# process each region 
for ((i=0; i<${#regions[@]}; i+=2)); do
    region_name=${regions[$i]}
    region_bbox=${regions[$i+1]}

    echo "Processing region: ${region_name}..."
    # snow processing pipeline taken from https://github.com/rainflame/pika-datasets/tree/master/layers/snow
    python quantize.py --bin-size=6 --bbox="${region_bbox}" --input-file="data/sources/snow-conus.tif" --output-file="data/temp/snow-quantized.tif"
    geopolygonize --input-file="data/temp/snow-quantized.tif" --output-file="data/temp/snow-contours.shp"
    bash tile_snow.sh

    echo "Uploading dataset..."
    # upload the output to this region's dir on r2
    rclone copy data/output/snow-meta.json r2:mapmeta/"${region_name}"/ --progress
    rclone copy data/output/snow.pmtiles r2:mapserve/"${region_name}"/ --progress

done

# delete the data directories 
rm -rf data/sources/ && rm -rf data/temp/ && rm -rf data/output/

echo -e "--- DONE BUILDING SNOW DATASET AT [$(date +'%Y-%m-%d %H:%M:%S')] ---\n"
