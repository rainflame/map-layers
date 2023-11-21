# Dynamic Layers

These layers are built from sources that update at least daily. They're generated in much the same way as the layers in [`/basemap`](/basemap/) except they aren't all combined into a single `pmtiles` archive when complete; each layer is served from a separate file. This allows us to only update a single layer when it's rebuilt, rather than needing to update the entire `pmtiles` archive.

Each layer contains instructions for building it. The scripts that run as cronjobs to rebuild the layers periodically can be found in [`/builders`](/builders/).
