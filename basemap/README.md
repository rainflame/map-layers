# Basemap

The general purpose basemap.

## Fonts

We use [Barlow](https://github.com/jpt/barlow) as the map's font.

Maplibre-gl requires a series of `.pbf` files to render text. Use [font maker](https://maplibre.org/font-maker/) to convert `Barlow Regular`, and download. Unzip and move the `Barlow Regular` directory of `.pbf` files to `/data`. You should have something like:

```
data/
    Barlow Regular/
        0-255.pbf
        256-511.pbf
        512-767.pbf
        ...
```
