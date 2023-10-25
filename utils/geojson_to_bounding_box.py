import geojson
import click

from shapely.geometry import shape


@click.command()
@click.option(
    "--input-file",
    default="data/output/bbox.geojson",
    help="The geojson file to convert to a bounding box",
)
def cli(input_file):
    with open(input_file) as f:
        geojson_str = f.read()

    geojson_obj = geojson.loads(geojson_str)
    shapely_geometry = shape(geojson_obj["features"][0]["geometry"])

    # get the max and min x and y values from the geojson
    bbox = shapely_geometry.envelope
    bbox_coords = list(bbox.exterior.coords)

    minx = min([coord[0] for coord in bbox_coords])
    miny = min([coord[1] for coord in bbox_coords])
    maxx = max([coord[0] for coord in bbox_coords])
    maxy = max([coord[1] for coord in bbox_coords])

    print("Bounding box: {},{},{},{}".format(minx, miny, maxx, maxy))


if __name__ == "__main__":
    cli()
