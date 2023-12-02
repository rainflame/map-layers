#!/bin/bash

OVERPASS_API_URL="https://overpass-api.de/api/interpreter"
QUERY="[out:xml][bbox:$1];$2;out body;"

echo "$QUERY"

curl -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "data=$QUERY" \
    "$OVERPASS_API_URL"\
    --output data/sources/extract.osm

# python flatten_members.py

# convert to .pbf
osmium cat -o data/sources/extract.osm.pbf data/sources/extract.osm --overwrite
