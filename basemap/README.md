# Basemap tile generation

Generate the basemap tiles. See each subdirectory for instructions on how to build that layer.

## Combining tiles

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
tile-join -o data/output/basemap.pmtiles glaciers/data/output/glaciers.pmtiles data/output/basemap.pmtiles --force
```

Any of the vector layers you've generated in the basemap directory can be combined together. The only exception is `elevation/data/output/elevation.pmtiles` that is raster data and therefore must be loaded in Maplibre-gl as its own layer.

## Deploy

On R2, we save each newly generated basemap as: `{map_region}/basemap/{date}_{uuid}.pmtiles` and elevation as `{map_region}/elevation/{date}_{uuid}.pmtiles` The deploy script will upload the basemap for a particular region in this format; pass in the provider, bucket, and map region as the first argument and names of files to upload as second and optional third arguments:

```
./deploy_basemap.sh r2:mapserve/central_oregon basemap elevation
```
