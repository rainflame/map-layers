# Elevation tiles

![Raw terrain RGB tiles](./elevation.png)

Here we create [TerrainRGB](https://docs.mapbox.com/data/tilesets/reference/mapbox-terrain-rgb-v1/) tiles from USGS DEM source files. TerrainRGB tiles are webp image tiles that can be loaded in Maplibre-gl and dynamically rendered as hillshade, used to calculate a viewshed, or display an elevation profile across a line.

In addition to TerrainRGB tiles, we also include a method for generating contour lines from the DEM sources. While you can [generate contours on the client from TerrainRGB tiles](https://github.com/onthegomap/maplibre-contour), it's cleaner to prebuild them and serve them as vector tiles to keep things fast on the client.

We're using the [USGS seamless 1 arc-second dataset](https://www.usgs.gov/faqs/what-types-elevation-datasets-are-available-what-formats-do-they-come-and-where-can-i-download), which is medium resolution and good enough for most use cases. Each tile is about 50MB. There is a higher resolution 1/3 arc-second dataset that has tiles that are around 450MB. I haven't tried this dataset but it would likely require a very hefty machine to run the tiling process, which is already very memory intensive.

Note that this dataset is only available for North America, but if you wanted to generate tiles for other parts of the world the [NASA's SRTM dataset](https://www2.jpl.nasa.gov/srtm/) would probably work well.

## Download the elevation data

Install the dependencies:

```
pip install -r requirements.txt
```

If the GDAL python library isn't building, manually install it so the python version matches the version of GDAL that's installed on your system:

```
pip install GDAL==$(gdal-config --version)
```

Use the jupyter notebook `download_elevation_data.ipynb` to interactively download the DEM files from USGS for a particular region.

```
jupyter notebook download_elevation_data.ipynb
```

There's a few bounding boxes included in the notebook, but you'll probably want to add your own. This will download all the `.tif` DEM tiles for that region to `/data/sources/`.

Alternatively, you can just run the python script if you don't want the interactive version:

```
python download_elevation_data.py --workers=8 --bbox='-124.566244,46.864746,-116.463504,41.991794'
```

Set `--workers` to the number of workers that should be spawned to download data in parallel and `--bbox` to the bounding box of the region for which you want data.

## Build the TerrainRGB tiles

To convert the DEM source files to TerrainRGB, we'll need to first convert them to an RGB image format. For that we'll use [rasterio](https://rasterio.readthedocs.io/en/latest/index.html) and a tool from mapbox called [rio-rgbify](https://github.com/mapbox/rio-rgbify). This tool also tiles the data, so we'll end up with a `.mtiles` file that can be converted to a `.pmtiles` file we can use to serve tiles to the client.

### Build a virtual dataset

First, build a virtual dataset with GDAL. This allows us to use the DEMs in the tiling step below without needing to combine the source DEMs into one giant input file.

```
gdalbuildvrt -overwrite -srcnodata -9999 -vrtnodata -9999 data/dem.vrt data/sources/*.tif
```

### Convert to tiled RGB images

> [!IMPORTANT]
> This is an extremely memory-intensive operation if you're combining a very large set of DEM files. You will likely want to run this on a machine with as much RAM as possible.

We'll use `rgbify` to convert the DEM sources into RGB images and build a tiled `.mbtiles` file:

```
rio rgbify -b -10000 -i 0.1 --min-z 1 --max-z 12 -j 10 --format webp data/dem.vrt data/rgb.mbtiles
```

Note that you'll want to change the number of workers in this command (`-j 10` in the example above) to an appropriate number given your machine's number of CPU cores.

As mentioned above, this is a very memory-intensive process. For reference, using a bounding box around the U.S. state of Oregon (3.2 GB of DEM files), `rgbify` used about 11.2 GB of RAM (3.5x more than the sources) to create a 1.8GB `.mbtiles` file. Using a bounding box around the entire continental U.S. (112GB of DEM files), it used about 215GB of RAM and 450GB of swap to create a 27GB `.mbtiles` file.

You'll most likely need to increase your swapfile size, which is done like this on Ubuntu:

```
sudo swapoff /swapfile
# increase the swapfile size. For the continental U.S. I created a 500GB swapfile
sudo fallocate -l 16G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

Note that I ran into [this issue](https://github.com/mapbox/rio-rgbify/issues/39) when running `rgbify`, with the only workaround being to manually edit the source code to remove the buggy line as [shown here](https://github.com/acalcutt/rio-rgbify/commit/6db4f8baf4d78e157e02c67b05afae49289f9ef1).

### Add metadata

`rgbify` does not add any metadata to the `.mbtiles` file beyond the bare minimum required fields. However, we'll want the bounding box coordinates included when converting to `.pmtiles`, otherwise they'll be set to 0 and the data will never be rendered.

Run this script to pull out the bounding box coordinates and add it to the `.mbtiles` file metadata:

```
python add_metadata.py
```

### Convert to `pmtiles`

Finally, convert to a `.pmtiles` file:

```
pmtiles convert data/rgb.mbtiles data/elevation.pmtiles
```

## Build the contour tiles

Contours are created by iterating over the DEM source files and running `gdal_contour` to create 40ft contours for the file region as geojson. Then, we use `tippecanoe` to combine the geojson contours into tiles.

### Create contours

Run the python script to generate geojson contours for each tile in `data/`:

```
python create_contours.py --workers=8
```

Use `--workers` to specify the number of workers you want to spawn to run the processing in parallel.

### Tile contours and clean up

Run the tiling and clean up steps:

```
./tile_contours.sh
```

Now you should have `contours_40ft.pmtiles`!

## Rendering it

Now you should be able to load the TerrainRGB elevation data in Maplibre-gl. For example, to render hillshade you can add a new layer:

```
{
    type: "raster-dem",
    url: `pmtiles://http://localhost:8080/elevation.pmtiles`,
    tileSize: 512,
}
```

and render it with a style spec like this:

```
{
  id: "hillshade",
  type: "hillshade",
  source: "elevation",
  paint: {
    "hillshade-exaggeration": 0.5,
    "hillshade-shadow-color": "#5a5a5a",
    "hillshade-highlight-color": "#FFFFFF",
    "hillshade-accent-color": "#5a5a5a",
    "hillshade-illumination-direction": 335,
    "hillshade-illumination-anchor": "viewport",
}
```
