# Utilities

Some general utilities that may be helpful for generating and manipulating datasets.

## Install

Install the python dependencies:

```
pip install -r requirements.txt
```

## Bounding box to GeoJSON

This tool creates a geojson file with a polygon representing a particular region, which can be useful for creating pmtiles extracts.

Run:

```
python bounding_box_to_geojson.py --bbox="-122.04976264563147,43.51921441989123,-120.94591116755655,44.39466349563759"
```

which should produce `data/output/bbox.geojson`.
