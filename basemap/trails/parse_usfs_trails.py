import fiona
import click
import os


@click.command()
@click.option(
    "--input-file",
    type=click.Path(file_okay=True, dir_okay=True),
    help="The input .gdb file",
    default="data/sources/S_USA.TrailNFS_Publish.gdb",
)
@click.option(
    "--output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for path lines",
    default="data/temp/snow_trails.gpkg",
)
@click.option(
    "--bbox",
    type=click.STRING,
    help="Bounding box to filter paths",
    default="-123.417224,43.022586,-118.980589,45.278084",
)
def cli(input_file, output_file, bbox):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # read the input file
    with fiona.open(input_file, layer="TrailNFS_Publish") as src:
        bbox = tuple(float(x) for x in bbox.split(","))
        filtered = src.filter(bbox=bbox)

        snow_trails = []

        print("Filtering and parsing snow trails...")
        for feature in filtered:
            # only interested in snow trails
            if feature["properties"]["TRAIL_TYPE"] == "SNOW":
                properties = {
                    "id": feature["properties"]["GLOBALID"],
                    "name": feature["properties"]["TRAIL_NAME"],
                    "ref": feature["properties"]["TRAIL_NO"],
                    "surface": feature["properties"]["TRAIL_SURFACE"],
                    "dog": None,
                    "bicycle": None,
                    "horse": None,
                    "bridge": None,
                    "snowmobile": feature["properties"]["SNOWMOBILE_MANAGED"] != None,
                    "snowshoe": feature["properties"]["SNOWSHOE_MANAGED"] != None,
                    "xcski": feature["properties"]["XCOUNTRY_SKI_MANAGED"] != None,
                    "groomed": None,  # TODO: figure out how to get this
                }

                # split the geometry into LineStrings if it's a multiLineString
                if feature["geometry"]["type"] == "MultiLineString":
                    for line in feature["geometry"]["coordinates"]:
                        snow_trails.append(
                            {
                                "geometry": {
                                    "type": "LineString",
                                    "coordinates": line,
                                },
                                "properties": properties,
                            }
                        )
                else:
                    snow_trails.append(
                        {
                            "geometry": feature["geometry"],
                            "properties": properties,
                        }
                    )

        trail_schema = {
            "geometry": "LineString",
            "properties": {
                "id": "int",
                "ref": "str",
                "name": "str",
                "surface": "str",
                "bridge": "bool",
                "bicycle": "bool",
                "horse": "bool",
                "dog": "bool",
                "snowmobile": "bool",
                "snowshoe": "bool",
                "xcski": "bool",
                "groomed": "bool",
            },
        }

        print("Saving trails...")
        with fiona.open(
            output_file, "w", driver="GPKG", crs="EPSG:4326", schema=trail_schema
        ) as output:
            for path in snow_trails:
                output.write(path)


if __name__ == "__main__":
    cli()
