# OpenStreetMap base vector tiles

To create the vector tiles, we use [planetiler](https://github.com/onthegomap/planetiler) to build them from OSM data. Follow the instructions in the planetiler repository to set up the project.

Here's the command to generate the vector tiles for a given [geofabrik](https://download.geofabrik.de/) area, in this case the western United States. This will download the area as a `.osm.pbf` file and convert it into tiles.

```
java -Xmx3g -jar planetiler.jar --download --area=us-west --output=us-west.pmtiles
```

Now, you should have a `.pmtiles` file that can be read from Maplibre-gl.
