# Waterways

Lakes and rivers sourced from openstreetmap data.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

Use the provided osm download utility to download data from the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). Pass in the bounding box as the first argument, ensuring that the boxes' corners are in the format lat, long. The second argument is the Overpass API query `(way[waterway];>;nwr[natural=water];>;)`, which selects the required relations and ways, plus their nodes.

```
./../../utils/download_osm.sh \
    "43.51921441989123,-122.04976264563147,44.39466349563759,-120.94591116755655" \
    "(way[waterway];>;nwr[natural=water];>;)"
```

Now you should have the data at `data/sources/extract.osm.pbf`.

## Create geometries

To convert the openstreetmap data into polygons and lines, run:

```
python parse_waterways.py
```

Now you should have water and waterways files at `data/temp/water.gpkg` and `data/temp/waterways.gpkg`.

## Tile

Now we can create a tiled version of the water polygons and lines:

```
./tile_waterways.sh
```

Now you should have `data/output/water.pmtiles` and `data/output/waterways.pmtiles`.
