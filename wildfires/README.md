# Pika Wildfires

Historical U.S. wildfires.

## Building the dataset

There are three datasets that are combined to create the final fire perimeters layer.

- [USFS Fine Fire Perimeter Feature Layer](https://data-usfs.hub.arcgis.com/datasets/usfs::national-usfs-final-fire-perimeter-feature-layer/about). This contains historic and more recent wildfire boundaries for events > 10 acres on USFS-managed lands.
- [BLM National Fire Perimeters](https://gbp-blm-egis.hub.arcgis.com/datasets/BLM-EGIS::blm-natl-fire-perimeters-polygon/about). This dataset contains historic data up to 2020 for fires on BLM-managed lands.
- [WFIGS Interagency Fire Perimeters](https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters/about). This is the most authoritative dataset that contains fire perimeters on all fires in the United States starting in 2021.

Download shapefiles from the above links and place them in a `/data/sources/` directory in the subdirectories `/USFSPerimeters`, `/BLMPerimeters`, and `/NIFCPerimeters`. You should have a directory structure like this:

```
data/
    sources/
        USFSPerimeters/
            *.shp
            *.dbf
            *.shx
            ...
        BLMPerimeters/
            *.shp
            *.dbf
            *.shx
            ...
        NIFCPerimeters/
            *.shp
            *.dbf
            *.shx
            ...
```

### Combining datasets

Install the dependencies and run the python script to combine the datasets into a single shapefile:

```
pip install -r requirements.txt
```

Then,

```
python create_combined_fire_dataset.py
```

This will likely take over an hour to run. When complete, you should now have a combined, cleaned and deduplicated version of the dataset at `data/fires.shp`.

#### Combining datasets interactively

You can also run the jupyter notebook for an interactive version of the same process:

```
pip install jupyter seaborn
```

Then,

```
jupyter notebook create_combined_fire_dataset.ipynb
```

### Tile the dataset

To run the tiling script, ensure you have [GDAL](https://gdal.org/), [tippecanoe](https://github.com/mapbox/tippecanoe), and [pmtiles](https://github.com/protomaps/PMTiles) installed.

Run the script to convert the shapefile to tiles stored in a `.pmtiles` file:

```
./create_fires_pmtiles.sh
```

Now you should have `data/fires.pmtiles`!
