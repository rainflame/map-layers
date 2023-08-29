# Pika datasets

The source code to generate the datasets available on [pikamaps.com](https://pikamaps.com). See each subdirectory for instructions on creating each individual dataset.

- [Basemap](/basemap/). The general-purpose map that appears below any other layers. This directory contains the method for creating the map from OpenStreetMap data and the required font files.
- [Layers](/layers/). Generators for any layers that can be visualized on top of the basemap.
  - [Wildfires](/wildfires/). A layer containing historic wildfires in the United States since 1900. A script is provided to merge a number of different datasets into one deduplicated and cleaned dataset.

Pika Maps uses [protomaps](https://protomaps.com/) to serve map tiles. Each dataset can be built as a `.pmtiles` file that can be deployed to Cloudflare or AWS and [served through a serverless function](https://protomaps.com/docs/cdn).

## Deploying datasets

The `.pmtiles` files are deployed to Cloudflare R2 using `rclone`. First, [install `rclone`](https://rclone.org/downloads/) and configure it for R2 following [these instructions](https://developers.cloudflare.com/r2/examples/rclone/). Name the provider `pikar2`.

Listing and creating buckets looks like this:

```
rclone tree pikar2:
```

```
rclone mkdir pikar2:mapserve
```

For Pika Maps, we use two buckets: `mapserve` for `.pmtiles` files and `mapmeta` for any other filetypes, such as `.json` or `.pbf` (for fonts). Each bucket has a corresponding Cloudflare worker that serves its content.

### Uploading and serving pmtiles data

For storing `.pmtiles` files, we use a bucket `mapserve`. Uploading looks like this:

```
rclone copy layers/wildfires/data/fires.pmtiles pikar2:mapserve --progress
```

See [workers](/workers/) for instructions on setting up the Cloudflare worker to serve files from the `mapserve` bucket.

### Uploading and serving other data

Other file types get uploaded to a bucket `mapmeta`. For example, uploading the font files looks like this:

```
rclone copy basemap/glypths/data/Barlow\ Regular pikar2:mapmeta/Barlow\ Regular/ --progress
```

See [workers](/workers/) for instructions on setting up the Cloudflare worker.
