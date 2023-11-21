# Layer builders

These scripts build the dynamic layers found in [/layers](/layers/). They're run as cronjobs on schedules that vary based on the availability of fresh data.

Each script will fetch the latest data, build the layer tiles, and upload it to Cloudflare R2.
