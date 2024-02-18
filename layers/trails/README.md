# Trails

Trails created from combined OSM and USFS data.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download trails from OSM

Use the provided osm download utility to download data from the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). Pass in the bounding box as the first argument, ensuring that the boxes' corners are in the format lat, long. The second argument is the Overpass API query `(way[highway=path];>;)`, which selects the required ways and their nodes.

```
./../../utils/download_osm.sh \
    "43.022586,-123.417224,45.278084,-118.980589" \
    "(way[highway=path];>;)"
```

Now you should have the data at `data/sources/extract.osm.pbf`.

## Create geometries

To convert the openstreetmap data into lines, run:

```
python parse_osm_paths.py
```

Now you should have paths at `data/temp/osm_paths.gpkg`.
