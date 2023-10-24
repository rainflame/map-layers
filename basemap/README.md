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

Ensure you have `tippecanoe` installed and run the `tile-join` utility to combine the vector datasets you've generated:

```
tile-join -o data/output/basemap.mbtiles elevation/data/output/contours.mbtiles glaciers/data/output/glaciers.mbtiles
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
