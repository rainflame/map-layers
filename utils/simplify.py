import click
import geojson
import os
import shapely

from tqdm import tqdm


def simplify_geometry(geom, tolerance):
    simplified_polygon = geom.simplify(tolerance, preserve_topology=True)
    return simplified_polygon


def simplify_geojson_geometries(input_file, output_file, tolerance):
    # check input exists
    if not os.path.exists(input_file):
        raise Exception(f"Cannot open {input_file}")

    # check path to output exists
    output_dir = os.path.dirname(output_file)
    if output_dir != "" and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "r") as f:
        gj = geojson.load(f)

    features = []
    for feature in tqdm(gj["features"]):
        geom = shapely.geometry.shape(feature["geometry"])
        simplified_polygon = simplify_geometry(geom, tolerance)
        feature["geometry"] = simplified_polygon
        features.append(feature)

    gj["features"] = features

    with open(output_file, "w") as f:
        geojson.dump(gj, f)


@click.command()
@click.option(
    "--input-file",
    help="The input geojson",
    required=True,
)
@click.option(
    "--output-file",
    help="The output geojson",
    required=True,
)
@click.option("--tolerance", default=0.0001, help="The tolerance for simplification.")
def cli(input_file, output_file, tolerance):
    simplify_geojson_geometries(input_file, output_file, tolerance)


if __name__ == "__main__":
    cli()
