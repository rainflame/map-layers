## Glyphs

We use [Barlow](https://github.com/jpt/barlow) as the map's font.

Maplibre-gl requires `.pbf` files to render text. Use [font maker](https://maplibre.org/font-maker/) to convert `Barlow Regular`, and download. Unzip the `Barlow Regular` directory, which should be composed of a series of `.pbf` files, like this:

```
Barlow Regular/
    0-255.pbf
    256-511.pbf
    512-767.pbf
    ...
```

These font files can be served from the [mapmeta](../../workers/mapmeta/) worker; upload the entire `Barlow Regular` directory to the `mapmeta` R2 bucket and the files will be accessible at `{MAPMETA_API_URL}/Barlow%20Regular/{range}.pbf`.
