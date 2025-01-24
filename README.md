# Rainflame map layers

A series of custom map layers. The source code for each layer is provided to download data, process, and produce a raster or vector `pmtiles` file.

The build pipelines we've developed are different than an integrated tool like [planetiler](https://github.com/onthegomap/planetiler) that's designed for building vector tiles from OSM data for very large regions. Instead, we've designed the processing for each layer around a specific data source for much smaller regions. Sources include public datasets provided by U.S. federal and state agencies and OpenStreetMap.

Each pipeline contains a number of layer-specifc build steps that progressively transform that data for that layer using python and bash scripts. The pipelines utilize a variety of GIS tools including [GDAL](https://gdal.org/), [fiona](https://pypi.org/project/fiona/), [shapely](https://shapely.readthedocs.io/en/stable/), in addition to some custom tools we built like [geopolygonize](https://github.com/rainflame/geopolygonize/) and [geopolymid](https://github.com/rainflame/geopolymid). Once processing is complete, each build pipeline produces a geopackage file. We then use [tippecanoe](https://github.com/felt/tippecanoe) to tile the data into a [protomaps](https://protomaps.com/) `pmtiles` archive.

To run any of the layer build pipelines, first make sure you have [conda or mamba installed](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html).

Create the environment:

```
mamba env create -f environment.yml
```

Activate it:

```
mamba activate map-layers
```

Then follow the instructions below to build the layers:

- [Elevation](/layers/elevation/) (hillshading + contours)
- [Glaciers](/layers/glaciers/) (highest-resolution glacier polygons)
- [Waterways](/layers/waterways/) (lakes, rivers, canals, streams and so on)
- [Wildfires](/layers/wildfires/) (historic wildfire perimeters)
- [Landcover](/layers/landcover/) (polygons for 1000+ landcover classes)
- [Snow](/layers/snow/) (daily snowpack depth polygons)
- [Peaks](/layers/peaks/) (prominent points)
- [Trails](/layers/trails/) (hiking, snowshoeing, and cross country skiing trails)
