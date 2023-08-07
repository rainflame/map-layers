# Workers

These are the Cloudflare workers that serve data for Pika Maps.

## mapserve

This worker serves `.pmtiles` file requests. Start by updating the `pmtiles` submodule:

```
git submodule update --init --recursive
```

Then, find the Cloudflare worker in `mapserve/serverless/cloudflare`. Follow the [instructions here](https://protomaps.com/docs/cdn/cloudflare#alternative:-use-wrangler) to set it up.
