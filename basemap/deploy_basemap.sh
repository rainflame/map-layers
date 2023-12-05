#!/bin/bash

if [ -z "$1" ]; then
    echo "Provide a valid rclone remote as the first argument"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Provide one of 'elevation' or 'basemap' as the second argument"
    exit 1
fi

if [ "$2" != "basemap" ] && [ "$2" != "elevation" ]; then
    echo "Provide one of 'elevation' or 'basemap' as the second argument"
    exit 1
fi

if [ -n "$3" ]; then
    if [ "$3" != "basemap" ] && [ "$3" != "elevation" ]; then
        echo "Provide one of 'elevation' or 'basemap' as the third argument"
        exit 1
    fi
fi

current_date=$(date '+%Y-%m-%d')

if [ "$2" == "basemap" ] || [ "$3" == "basemap" ]; then
    short_uuid=$(uuidgen | tr -d '-' | cut -c 1-8)
    remote_path="$1"/basemap/"${current_date}"_"${short_uuid}".pmtiles
    echo "Deploying basemap to: $remote_path"
    rclone copyto --progress data/output/basemap.pmtiles "$remote_path"
fi
   

if [ "$2" == "elevation" ] || [ "$3" == "elevation" ]; then
    short_uuid=$(uuidgen | tr -d '-' | cut -c 1-8)
    remote_path="$1"/elevation/"${current_date}"_"${short_uuid}".pmtiles
    echo "Deploying elevation to: $remote_path"
    rclone copyto --progress elevation/data/output/elevation.pmtiles "$remote_path"

fi

echo "Done"