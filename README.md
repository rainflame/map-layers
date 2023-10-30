# Pika datasets

The source code to generate the datasets and maps available on [pikamaps.com](https://pikamaps.com).

## Building datasets

To build the datasets, activate the conda environment:

```
conda env create -f environment.yml
```

If you're going to build the vector basemap tiles, you'll also need Java 17+ installed.

Java installation on Linux:

```
sudo apt install openjdk-19-jre-headless
```

Each subdirectory has instructions for building each part of the dataset. See [basemap](/basemap/) for instructions on building the map tiles from OpenStreetMap, font files, and elevation data for hillshading. See [layers](/layers/) for additional layers that can be visualized on the basemap.

## Deploying datasets

Each dataset is a [protomaps](https://protomaps.com/) `.pmtiles` file. These files are stored on Cloudflare R2 and served through Cloudflare Workers functions. The [Pika Maps frontend](https://github.com/rainflame/pika-maps) is built with [Maplibre GL JS](https://maplibre.org/maplibre-gl-js/docs/), which is what requests the tiles from the Cloudflare worker and renders them.

### Uploading datasets to R2

The `.pmtiles` files can be deployed to Cloudflare R2 using `rclone`. First, [install `rclone`](https://rclone.org/downloads/) and configure it for R2 following [these instructions](https://developers.cloudflare.com/r2/examples/rclone/).

Listing and creating buckets looks like this:

```
rclone tree [provider name]:
```

```
rclone mkdir [provider name]:[bucket name]
```

For Pika Maps, we use two buckets: `mapserve` for serving `.pmtiles` files and `mapmeta` for serving any other filetypes, such as `.json` or `.pbf` (for fonts). Each bucket has a corresponding Cloudflare worker that serves its content.

For storing `.pmtiles` files, we use a bucket `mapserve`. Uploading looks like this:

```
rclone copy layers/wildfires/data/fires.pmtiles [provider name]:mapserve --progress
```

Other file types get uploaded to a bucket `mapmeta`. For example, uploading the font files looks like this:

```
rclone copy basemap/glyphs/data/Barlow\ Regular pikar2:mapmeta/Barlow\ Regular/ --progress
```

### Serving the datasets

The code for the Cloudflare workers that serve the datasets from these buckets can be found in [workers](/workers/).

#### `mapserve` worker

This worker serves `.pmtiles` file requests from the `mapserve` bucket. Start by installing the protomaps submodule:

```
git submodule update --init --recursive
```

Then, find the Cloudflare worker in `mapserve/serverless/cloudflare`. Follow the [instructions here](https://protomaps.com/docs/cdn/cloudflare#alternative:-use-wrangler) to set it up.

#### `mapmeta` worker

This worker serves `.json` and font `.pbf` files from the `mapmeta` bucket. It can be installed using the same instructions as the `mapserve` worker.
