import click
import os

import fiona


@click.command()
@click.option(
    "--bbox",
    default="-124.566244,46.864746,-116.463504,41.991794",
    help="Bounding box to trim the source shapefile.",
)
@click.option(
    "--filter-names",
    default="",
    help="A comma separated list of glacier names to filter and set to NULL.",
)
@click.option(
    "--filter-year",
    default=2023,
    help="The year to filter the glacier data. Any glaciers with a year greater than this will be removed.",
)
@click.option(
    "--input-file",
    default="data/sources/glims_polygons.shp",
    help="The input shapefile to trim and filter.",
)
@click.option(
    "--output-file",
    default="data/temp/glaciers.gpkg",
    help="The output geopackage file.",
)
def cli(bbox, filter_names, filter_year, input_file, output_file):
    # make sure the path to the output exists, and if not make it
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xmin, ymin, xmax, ymax = [float(x) for x in bbox.split(",")]
    name_blacklist = filter_names.split(",")

    with fiona.open(input_file) as src:
        print("Filtering glaciers by bbox...")
        clipped = src.filter(bbox=(xmin, ymin, xmax, ymax))

        print("Filtering glaciers by year...")
        filtered = []
        for feature in clipped:
            new_feat = {
                "geometry": feature["geometry"],
                "properties": {},
            }
            # verify the anlys_time is greater than or equal to the filter year
            # format will be like 2023-02-16T00:00:00
            if "anlys_time" in feature["properties"]:
                anlys_time = feature["properties"]["anlys_time"]
                anlys_year = int(anlys_time.split("-")[0])
                if anlys_year < int(filter_year):
                    continue
                else:
                    new_feat["properties"]["anlys_time"] = anlys_time
            else:
                continue

            # filter out any names in the blacklist
            if "glac_name" in feature["properties"]:
                glac_name = feature["properties"]["glac_name"]
                if glac_name in name_blacklist:
                    new_feat["properties"]["glac_name"] = None
                else:
                    new_feat["properties"]["glac_name"] = glac_name

            # add the area
            if "area" in feature["properties"]:
                new_feat["properties"]["area"] = feature["properties"]["area"]

            filtered.append(new_feat)

        print(f"Saving {len(filtered)} glaciers...")
        # write the filtered features to the output file
        with fiona.open(
            output_file,
            "w",
            driver="GPKG",
            crs=src.crs,
            schema={
                "geometry": "Polygon",
                "properties": {
                    "glac_name": "str",
                    "area": "float",
                    "anlys_time": "str",
                },
            },
        ) as dst:
            dst.writerecords(filtered)


if __name__ == "__main__":
    cli()
