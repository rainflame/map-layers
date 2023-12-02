# Utilities

Some general utilities that may be helpful for generating and manipulating datasets.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

## Polygons to weighted medial axes

Here we take a geojson file of polygons and produce a series of lines representing their approximate [medial axes](https://en.wikipedia.org/wiki/Medial_axis). This will not produce the exact medial axis, but rather an approximation that passes through the most visually bulky sections of the polygon. Any properties of the original polygons are preserved in the output lines.

```
python polygons_to_weighted_medial_axes.py --input-file="data/input/lakes.geojson" --output-file="data/output/lake_axes.geojson"
```

## Simplify Polygons or Lines

Take a geojson file of lines or polygons and produces a simplified version of them using a topology-preserving version of the [Douglas-Peucker algorithm](https://en.wikipedia.org/wiki/Ramer%E2%80%93Douglas%E2%80%93Peucker_algorithm). Any properties of the input features are preserved in the output.

```
simplify.py --input-file="data/input/axes.geojson" --output-file="data/output/axes-simple.geojson" --tolerance=0.0001
```

## Bounding box to GeoJSON

This tool creates a geojson file with a polygon representing a particular region, which can be useful for creating pmtiles extracts.

Run:

```
python bounding_box_to_geojson.py --bbox="-123.417224,43.022586,-118.980589,45.278084"
```

which should produce `data/output/bbox.geojson`.

## GeoJSON to bounding box

This tool assumes there's a geojson file with a single polygon feature. Get the bounding box:

```
python geojson_to_bounding_box.py --input-file="data/input/shape.geojson"
```

which should print something like `-123.417224,43.022586,-118.980589,45.278084`.

## Download OSM data

Download openstreetmap data from the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). Pass in the bounding box as the first argument, ensuring that the boxes' corners are in the format lat, long. Pass in an [overpass query](https://osm-queries.ldodds.com/syntax-reference.html) as the second argument.

```
./download_osm.sh \
    "43.51921441989123,-122.04976264563147,44.39466349563759,-120.94591116755655" \
    "(way[waterway];>;nwr[natural=water];>;)"
```

This should save the data to `data/sources/extract.osm.pbf`.
