# Wildfires

Historical U.S. wildfires.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

There are three datasets that are combined to create the final fire perimeters layer.

- [USFS Fine Fire Perimeter Feature Layer](https://data-usfs.hub.arcgis.com/datasets/usfs::national-usfs-final-fire-perimeter-feature-layer/about). This contains historic and more recent wildfire boundaries for events > 10 acres on USFS-managed lands.
- [BLM National Fire Perimeters](https://gbp-blm-egis.hub.arcgis.com/datasets/BLM-EGIS::blm-natl-fire-perimeters-polygon/about). This dataset contains historic data up to 2020 for fires on BLM-managed lands.
- [WFIGS Interagency Fire Perimeters](https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters/about). This is the most authoritative dataset that contains fire perimeters on all fires in the United States starting in 2021.

Manually download shapefiles from the above links and place them in a `/data/sources/` directory in the subdirectories `/USFSPerimeters`, `/BLMPerimeters`, and `/NIFCPerimeters`.

## Combine datasets

To combine the three datasets into a single file for a given bounding box region, run:

```
python combine_fire_datasets.py --bbox="-122.04976264563147,43.51921441989123,-120.94591116755655,44.39466349563759"
```

## Deduplicate

The datasets contain many duplicate fires that may have slightly different names and boundaries. This script identifies high-probability duplicates and removes them. It does this by identifying duplicates where all of the following are true for a pair of given boundaries:

- Have intersecting bounding boxes
- Are the same year
- Have areas within 20% of each other
- Have names with a [Jaro-Winkler](https://en.wikipedia.org/wiki/Jaro%E2%80%93Winkler_distance) similarity > 0.5
- Have an intersection that is at least 80% the overall area of at least one of the boundaries

Run the deduplication:

```
python deduplicate_fires.py
```

## Tile

Now we can create a tiled version of the boundaries:

```
./tile_fires.sh
```

Now you should have `data/output/wildfires.pmtiles`.
