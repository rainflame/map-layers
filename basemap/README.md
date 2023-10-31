# Basemap tile generation

Here we generate the basemap tiles from a variety of sources. See each subdirectory for information on how to build each part of the basemap.

## Combining tiles

Once you've generated datasets, you should have a series of `.mbtiles` files like:

```
elevation/
    data/
        output/
            contours.mbtiles
glaciers/
    data/
        output/
            glaciers.mbtiles
```

and so on. We're going to combine them into one single `.mbtiles` file.

First, create the output directory:

```
mkdir -p data/output/
```

To combine all layers you've generated, run:

```
./tile_layers.sh
```

Or, to add one or two layers to an existing basemap, run:

```
tile-join -o data/output/basemap.mbtiles glaciers/data/output/glaciers.mbtiles data/output/basemap.mbtiles --force
```

The exception is `elevation/data/output/elevation.mbtiles` that is raster data and therefore must be loaded in Maplibre-gl as its own layer.

Then, run `pmtiles` to generate a `.pmtiles` archive:

```
pmtiles convert data/output/basemap.mbtiles data/output/basemap.pmtiles
```

You should now have the final output files:

```
data/output/
    basemap.mbtiles
    basemap.pmtiles
```
