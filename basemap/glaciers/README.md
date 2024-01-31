# Glacier Boundaries

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

Download the latest version of the GLIMS dataset [here](https://daacdata.apps.nsidc.org/pub/DATASETS/nsidc0272_GLIMS_v1/). The filename should be something like `NSIDC-XXXX_glims_db_north_YYYYMMDD_vXXX.zip`. Extract it to `data/sources/`. The file we're going to use is `glims_polygons.shp`.

## Build the dataset

This dataset contains multiple glacier boundaries at different timestamps that capture the glaciers' change over time. We're only interested in the latest here, so we'll filter out any boundaries older than a certain date.

```
python filter_glaciers.py \
    --input-file="data/sources/glims_polygons.shp" \
    --output-file="data/temp/glaciers-filtered.gpkg" \
    --bbox="-123.417224,43.022586,-118.980589,45.278084" \
    --filter-year=2023 \
    --filter-names="OR,unknown,NONE"
```

## Combine glaciers

The dataset includes glaciers that share edges. In cases that the intersecting glaciers have the same name, or one of them is named and the other is not we combine them.

```
python combine_glaciers.py \
    --input-file="data/temp/glaciers-filtered.gpkg" \
    --output-file="data/temp/glaciers.gpkg"
```

## Create label lines

To place labels over glaciers, we've built a tool called [geopolymid](https://github.com/rainflame/geopolymid). This tool will create smoothed lines that flow through the centers of each polygon and can be used to place a label.

See [geopolymid](https://github.com/rainflame/geopolymid) for instructions on how to create label lines.

Once complete, name the labels as `glacier-labels.gpkg` and place in `data/temp/glacier-labels.gpkg`.

## Tile the dataset

Now we can create a tiled version of the boundaries:

```

./tile_glaciers.sh

```

You should now have the final output file at `data/output/glaciers.pmtiles`
