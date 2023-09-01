# Elevation tiles

![Raw terrain RGB tiles](./elevation.png)

Create TerrainRGB tiles from USGS DEM sources.

## Building the elevation dataset

Install the dependencies:

```
pip install -r requirements.txt
```

### Download the elevation data

We're using the [USGS seamless 1 arc-second dataset](https://www.usgs.gov/faqs/what-types-elevation-datasets-are-available-what-formats-do-they-come-and-where-can-i-download), which is medium resolution and good enough for most use cases. Each tile is about 50MB. There is a higher resolution 1/3 arc-second dataset that has tiles that are around 450MB. I haven't tried this dataset but it would likely require a very hefty machine to run the tiling process below, which is already very memory intensive.

Use the jupyter notebook `download_elevation_data.ipynb` to interactively download the DEM files from USGS for a particular region.

```
jupyter notebook download_elevation_data.ipynb
```

There's a few bounding boxes included in the notebook, but you'll probably want to add your own. This will download all the `.tif` DEM tiles for that region to `/data/sources/`.

Alternatively, you can just run the python script if you don't want the interactive version. Be sure to set your bounding box in the script, then run it:

```
python download_elevation_data.py
```

### Convert to tiles

To tile the dataset, you'll need GDAL installed, along with [rasterio](https://rasterio.readthedocs.io/en/latest/index.html) and [rio-rgbify](https://github.com/mapbox/rio-rgbify).

Note that I ran into [this issue](https://github.com/mapbox/rio-rgbify/issues/39) when running `rgbify`, with the only workaround being to manually edit the source code to remove the buggy line as [shown here](https://github.com/acalcutt/rio-rgbify/commit/6db4f8baf4d78e157e02c67b05afae49289f9ef1). Hopefully this gets fixed in the future, but as of the time of writing this the workaround is necessary.

#### Build a virtual dataset

First, build a virtual dataset with GDAL. This allows us to use the DEMs in the tiling step below without needing to combine the source DEMs into one giant input file.

```
gdalbuildvrt -overwrite -srcnodata -9999 -vrtnodata -9999 data/dem.vrt data/sources/*.tif
```

#### Convert to tiled RGB images

> [!IMPORTANT]
> This is an extremely memory-intensive operation if you're combining a very large set of DEM files. You will likely want to run this on a machine with as much RAM as possible.

We'll use `rgbify` to convert the DEM sources into RGB images and build a tiled `.mbtiles` file:

```
rio rgbify -b -10000 -i 0.1 --min-z 6 --max-z 12 -j 10 --format webp data/dem.vrt data/rgb.mbtiles
```

Note that you'll want to change the number of workers in this command (`-j 10` in the example above) to an appropriate number given your machine's number of CPU cores.

As mentioned above, this is a very memory-intensive process. For reference, using a bounding box around the U.S. state of Oregon (3.2 GB of DEM files), `rgbify` used about 11.2 GB of RAM (3.5x more than the sources) to create a 1.8GB `.mbtiles` file.

I was running into issues on my machine that were solved by increasing the swapfile size, which is done like this on Ubuntu:

```
sudo swapoff /swapfile
sudo fallocate -l 16G /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Add metadata

`rgbify` does not add any metadata to the `.mbtiles` file beyond the bare minimum required fields. However, we'll want the bounding box coordinates included when converting to `.pmtiles`, otherwise they'll be set to 0 and the data will never be rendered.

Run this script to pull out the bounding box coordinates and add it to the `.mbtiles` file metadata:

```
python add_metadata.py
```

#### Convert to `pmtiles`

Finally, convert to a `.pmtiles` file:

```
pmtiles convert data/rgb.mbtiles data/elevation.pmtiles
```

## Rendering it

Now you should be able to load the elevation data in Maplibre-gl. For example, to render hillshade you can add a new layer:

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
