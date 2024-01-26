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
    "43.022586,-123.417224,45.278084,-118.980589" \
    "(way[waterway];>;nwr[natural=water];>;)"
```

Now you should have the data at `data/sources/extract.osm.pbf`.

## Create geometries

To convert the openstreetmap data into polygons and lines, run:

```
python parse_waterways.py
```

Now you should have water and waterways files at `data/temp/water.gpkg` and `data/temp/waterways.gpkg`.

## Create label lines

To place labels over water bodies such as lakes and reservoirs, we've built a tool called [geopolymid](https://github.com/rainflame/geopolymid). This tool will create smoothed lines that flow through the centers of each polygon and can be used to place a label.

First, filter the water dataset so only water bodies of the correct type that have names are included:

```
ogr2ogr \
    -f GPKG \
    data/temp/water-no-rivers.gpkg \
    data/temp/water.gpkg \
    -where "(type != 'river' OR type IS NULL) AND name IS NOT NULL"
```

See [geopolymid](https://github.com/rainflame/geopolymid) for instructions on how to create label lines.

Once complete, name the labels as `water-labels.gpkg` and place in `data/temp/water-labels.gpkg`.

## Tile

Now we can create a tiled version of the water polygons and lines:

```
./tile_waterways.sh
```

Now you should have `data/output/water.pmtiles`, which combines the water polygons, water labels, and waterway lines.
