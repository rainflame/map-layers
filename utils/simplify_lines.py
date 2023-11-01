# given a geojson file, simplify the lines and output a new geojson file

import click
import geojson
import os
import shapely
from simplification.cutil import simplify_coords_vwp

from shapely.geometry import LineString
from tqdm import tqdm


def simplify_line_coordinates(coords, tolerance):
    simplified_coords = simplify_coords_vwp(coords, tolerance)
    simplified_line = LineString(simplified_coords)

    return simplified_line


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
        if geom.geom_type == "LineString":
            simplified_line = simplify_line_coordinates(
                feature["geometry"]["coordinates"], tolerance
            )
            feature["geometry"] = simplified_line
            features.append(feature)
        elif geom.geom_type == "MultiLineString":
            # get the coords from the points in the line
            coords = []
            for sub_coords in feature["geometry"]["coordinates"]:
                coords.extend(sub_coords)
            simplified_coords = simplify_line_coordinates(coords, tolerance)
            simplified_line = LineString(simplified_coords)
            feature["geometry"] = simplified_line
            features.append(feature)

        else:
            raise Exception(f"Unexpected geometry type: {geom.geom_type}")

    with open(output_file, "w") as f:
        geojson.dump(geojson.FeatureCollection(features), f)


if __name__ == "__main__":
    cli()
