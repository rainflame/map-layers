# Glacier Boundaries

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

Download the latest version of the GLIMS dataset [here](https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0272_GLIMS_v1/). Extract it to `data/sources/`. The file we're going to use is `glims_polygons.shp`.

## Build the dataset

This dataset contains multiple glacier boundaries at different timestamps that capture the glaciers' change over time. We're only interested in the latest here, so we'll filter out any boundaries older than a certain date.

```
python filter_glaciers.py \
    --input-file="data/sources/glims_polygons.shp" \
    --output-file="data/temp/glaciers-filtered.gpkg" \
    --bbox="-122.04976264563147,43.51921441989123,-120.94591116755655,44.39466349563759" \
    --filter-year=2023 \
    --filter-names="OR,unknown,NONE"
```

## Combine glaciers

The dataset includes glaciers that share edges. In cases that the intersecting glaciers have the same name, or one of them is named and the other is not we combine them.

```
python combine_glaciers.py \
    --input-file="data/temp/glaciers-filtered.gpkg" \
    --output-file="data/output/glaciers.gpkg"
```

## Create polygon centerlines

Next, we create the lines that we'll use to place the labels when rendering the map. We're going to approximate the [medial axis](https://en.wikipedia.org/wiki/Medial_axis) by creating a [skeleton](https://scikit-geometry.github.io/scikit-geometry/skeleton.html) for each polygon, then choosing the longest set of lines as the medial axis. This has the effect of creating a long centerline down each polygon.

```
python clean_and_label_glaciers.py
```

## Tile the dataset

Now we can create a tiled version of the boundaries:

```
./tile_glaciers.sh
```

You should now have the final output files:

```
data/output/
    glaciers.mbtiles
    glaciers.pmtiles
```
