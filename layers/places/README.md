# Places

Points representing developed areas.

## Install

Ensure you've [activated the conda environment](../../README.md#building-datasets).

Create the data directories:

```
mkdir -p data/sources/ && mkdir -p data/temp/ && mkdir -p data/output/
```

## Download data

### OSM data

Use the provided osm download utility to download data from the [Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API). Pass in the bounding box as the first argument, ensuring that the boxes' corners are in the format lat, long. The second argument is the Overpass API query which selects the required relations and ways, plus their nodes.

```
./../../utils/download_osm.sh \
    "43.022586,-123.417224,45.278084,-118.980589" \
    "(nwr[place];>;nwr["boundary"];>;nwr[leisure=nature_reserve];>;nwr[leisure=park];>;nwr[leisure=dog_park];>;)"
```

Now you should have the OSM data at `data/sources/extract.osm.pbf`.

### BLM boundaries

BLM boundaries are not included in OSM data, so we'll download them separately. These can be found on the BLM's GIS site, for example here is the file for [Oregon](https://gbp-blm-egis.hub.arcgis.com/datasets/BLM-EGIS::blm-or-management-ownership-dissolve-polygon-hub/about_).

Download as a geopackage and save in `/data/sources`.

This file contains land ownership data information for a variety of juristictions besides the BLM. To reduce it so it only contains BLM boundaries, run this GDAL command:

```
ogr2ogr \
    -f "GPKG" \
    data/temp/BLM.gpkg \
    data/sources/BLM_ownership.gpkg \
    -where "PROPERTY_STATUS = 'BLM'"
```

## Create geometries

To convert the openstreetmap data into polygons and lines, in addition to integrating the BLM boundaries, run:

```
python parse_places.py
```

Now you should have place point and polygons at `data/temp/place-points.gpkg` and `data/temp/place-polygons.gpkg`.

## Tile
