# Utilities

Some general utilities that may be helpful for generating and manipulating datasets.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

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
