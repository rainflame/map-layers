# Pika datasets

The source code to generate the map layers available on [pikamaps.com](https://pikamaps.com).

There's two primary components to Pika Maps: the basemap, and the dynamic layers. The basemap is built from a variety of public datasets provided by U.S. federal agencies and openstreetmap. It's built once and updated fairly infrequently. You can build the basemap from scratch by building the components listed in [basemap/](/basemap/), then combining them into a single [protomaps](https://protomaps.com/) `pmtiles` archive. This archive can then be rendered using [maplibre-gl](https://github.com/maplibre/maplibre-gl-js) or any other map rendering engine that supports `pmtiles` archives.

The dynamic layers are updated more often, at least daily depending on the layer. Their structure mirrors that of the basemap, the only difference is that once built each layer is kept as its own `pmtiles` archive and served individually. You can find the code to build these layers in [layers/](/layers/). We run the pipelines to build these layers as cronjobs.

## Building

To run any of the layer build pipelines, first make sure you have [conda or mamba installed](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html).

Create the environment:

```
mamba env create -f environment.yml
```

Activate the environment:
```
mamba activate pika-datasets
```

Then follow the instructions below to build any components of the basemap or dynamic layers:

- Basemap
  - [Elevation](/basemap/elevation/) (hillshading + contours)
  - [Glaciers](/basemap/glaciers/) (highest-resolution glacier polygons)
  - [Waterways](/basemap/waterways/) (lakes, rivers, canals, streams and so on)
  - [Wildfires](/basemap/wildfires/) (historic wildfire perimeters)
  - [Landcover](/basemap/landcover/) (polygons for 1000+ landcover classes)
- Layers
  - [Snow](/layers/snow/) (daily snowpack depth polygons)

### Combining basemap layers

Once you've created the layers you want to include in the basemap, you're ready to combine them into a single pmtiles file.

First, create the output directory:

```
mkdir -p data/output/
```

To combine all layers you've generated, run:

```
./tile_layers.sh
```

This will search for any built layers and create `data/output/basemap.pmtiles`.

Alternatively, you can manually add one or two layers to an existing basemap. For example, to add the glaciers layer to an existing basemap file, run:

```
tile-join -o data/output/basemap.pmtiles basemap/glaciers/data/output/glaciers.pmtiles data/output/basemap.pmtiles --force
```

Any of the vector layers you've generated in the basemap directory can be combined together. The only exception is `basemap/elevation/data/output/elevation.pmtiles` that is raster data and therefore must be loaded in Maplibre-gl as its own layer.
