# Natural POIs

Points of interest sourced from OSM data.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

Use the provided osm download utility to download data from the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). Pass in the bounding box as the first argument, ensuring that the boxes' corners are in the format lat, long. The second argument is the Overpass API query `(node[natural];>;)`, which selects the required nodes.

```
./../../utils/download_osm.sh \
    "43.022586,-123.417224,45.278084,-118.980589" \
    "(node[natural];>;)"
```

Now you should have the data at `data/sources/extract.osm.pbf`.

## Create peak points

To convert the openstreetmap data into points, run:

```
python parse_pois.py \
    --input-file="data/sources/extract.osm.pbf" \
    --output-file="data/temp/pois_natural.gpkg" \
    --to-feet
```

## Get peak prominence data

In order to determine which peaks should be shown at each zoom level, we use their [topographic prominence](https://en.wikipedia.org/wiki/Topographic_prominence). Peaks with a higher prominence are shown at lower zoom levels, while peaks with lower prominence are shown at higher zoom levels.

We use [Andrew Kirmse's prominence data](https://www.andrewkirmse.com/prominence-update-2023), which can be [downloaded here](https://github.com/akirmse/mountains#results). Move the unzipped prominence txt file to `data/sources`. Then run this script to associcate the peaks from the previous step with their prominence values:

```
python associate_prominence.py \
    --bbox="-123.417224,43.022586,-118.980589,45.278084" \
    --input-file="data/temp/pois_natural.gpkg" \
    --prominence-file="data/sources/all-peaks-sorted-p100.txt" \
    --output-file="data/temp/peaks_prominence.gpkg" \
    --to-feet
```

## Tile

Now we can create a tiled version of the peaks:

```
./tile_pois.sh
```

Now you should have `data/output/peaks.pmtiles`.
