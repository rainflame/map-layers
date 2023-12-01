#!/bin/bash

OVERPASS_API_URL="https://overpass-api.de/api/interpreter"
QUERY="[bbox:$1];(node;way;relation;);out geom;"

echo "$QUERY"

curl -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "data=$QUERY" \
    "$OVERPASS_API_URL"\
    --output data/sources/extract.osm

# convert to .pbf
osmium cat -o data/sources/extract.osm.pbf data/sources/extract.osm