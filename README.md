# Pika datasets

This is the source code used to generate the map tiles for [Pika Maps](https://pikamaps.com). We're releasing it publicly so anyone can see how the raw data sources are processed into a form that's more visually compelling. You should be able to run any of the pipelines in this repository and get data that's potentially useful for projects beyond just Pika Maps. However this is primarily an internal resource; it's provided as-is and we won't provide support for any additional features or use cases that aren't required by Pika Maps.

## Map layers

The build pipelines we've developed are fundamentally different than an integrated tool like [planetiler](https://github.com/onthegomap/planetiler) that's designed for building vector tiles from OSM data for very large regions. Instead, we've designed the processing for each layer around a specific data source for much smaller regions. Sources include public datasets provided by U.S. federal and state agencies and OpenStreetMap.

Each pipeline contains a number of layer-specifc build steps that progressively transform that data for that layer using python and bash scripts. The pipelines utilize a variety of GIS tools including [GDAL](https://gdal.org/), [fiona](https://pypi.org/project/fiona/), [shapely](https://shapely.readthedocs.io/en/stable/), in addition to some custom tools we built like [geopolygonize](https://github.com/rainflame/geopolygonize/) and [geopolymid](https://github.com/rainflame/geopolymid). Once processing is complete, each build pipeline produces a geopackage file. We then use [tippecanoe](https://github.com/felt/tippecanoe) to tile the data into a [protomaps](https://protomaps.com/) `pmtiles` archive.

To run any of the layer build pipelines, first make sure you have [conda or mamba installed](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html).

Create the environment:

```
mamba env create -f environment.yml
```

Activate it:

```
mamba activate pika-datasets
```

Then follow the instructions below to build the layers:

- [Elevation](/layers/elevation/) (hillshading + contours)
- [Glaciers](/layers/glaciers/) (highest-resolution glacier polygons)
- [Waterways](/layers/waterways/) (lakes, rivers, canals, streams and so on)
- [Wildfires](/layers/wildfires/) (historic wildfire perimeters)
- [Landcover](/layers/landcover/) (polygons for 1000+ landcover classes)
- [Snow](/layers/snow/) (daily snowpack depth polygons)
