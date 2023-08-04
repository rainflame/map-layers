# Pika datasets

The source code to generate the datasets available on [pikamaps.com](https://pikamaps.com). See each subdirectory for instructions on creating each individual dataset.

## Deploying a dataset

The `.pmtiles` files are deployed to Cloudflare R2 using `rclone`. First, [install `rclone`](https://rclone.org/downloads/) and configure it for R2 following [these instructions](https://developers.cloudflare.com/r2/examples/rclone/). Name the provider `pikar2`.

Listing and creating buckets looks like this:

```
rclone tree pikar2:
```

```
rclone mkdir pikar2:wildfires
```

Upload a `.pmtiles` file:

```
rclone copy wildfires/data/fires.pmtiles pikar2:wildfires --progress
```

To set up the Cloudflare worker to serve the data, follow the [instructions here](https://protomaps.com/docs/cdn/cloudflare).
