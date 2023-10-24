import geojson
import click
import os

from shapely.geometry import Polygon


@click.command()
@click.option(
    "--bbox",
    default="-124.566244,46.864746,-116.463504,41.991794",
    help="Bounding box to create a polygon",
)
def cli(bbox):
    # create data/output/ dir if it doesn't already exist
    if not os.path.exists("data/output"):
        os.makedirs("data/output")

    bbox_coords = list(map(float, bbox.split(",")))
    minx, miny, maxx, maxy = bbox_coords

    polygon = Polygon(
        [(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy), (minx, miny)]
    )

    feature = geojson.Feature(geometry=polygon, properties={})
    geojson_str = geojson.dumps(feature, sort_keys=True)

    # save the geojson to a file data/output/bbox.geojson
    with open("data/output/bbox.geojson", "w") as f:
        f.write(geojson_str)

    print("Done, created data/output/bbox.geojson")


if __name__ == "__main__":
    cli()
