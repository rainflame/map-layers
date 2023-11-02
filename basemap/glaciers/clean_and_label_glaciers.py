import click
import geojson
import multiprocessing
import os
import sys
import uuid

from shapely.geometry import Polygon
from rtree import index
from tqdm import tqdm

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, "..", "..", "utils"))

from polygons_to_weighted_medial_axes import weighted_medial_axes_from_geojson
from simplify import simplify_geojson_geometries


@click.command()
@click.option(
    "--input-file",
    help="The input geojson",
    default="data/temp/glaciers.geojson",
)
@click.option(
    "--cleaned-glaciers-output-file",
    help="The output geojson",
    default="data/temp/glaciers-cleaned.geojson",
)
@click.option(
    "--labels-output-file",
    help="The output geojson",
    default="data/temp/glacier-labels.geojson",
)
@click.option(
    "--pre-simplify-tolerance",
    default=0.0001,
    help="The tolerance for simplification of the input glaciers.",
)
@click.option(
    "--medial-axes-tolerance",
    default=0.0001,
    help="The tolerance for simplification of medial axes.",
)
def cli(
    input_file,
    cleaned_glaciers_output_file,
    labels_output_file,
    pre_simplify_tolerance,
    medial_axes_tolerance,
):
    print("Combining glaciers with the same name...")
    # load the input geojson
    with open(input_file, "r") as f:
        gj = geojson.load(f)

    polygons = {}

    # load the polygons into an rtree
    idx = index.Index()
    for polygon in gj["features"]:
        poly = Polygon(polygon["geometry"]["coordinates"][0])
        new_id = uuid.uuid4().int
        polygons[new_id] = {
            "polygon": poly,
            "id": new_id,
            "properties": polygon["properties"],
        }
        idx.insert(
            new_id,
            poly.envelope.bounds,
            obj=polygons[new_id],
        )

    unchecked_ids = [poly_id for poly_id in polygons]

    while len(unchecked_ids) > 0:
        poly_id = unchecked_ids.pop()

        if poly_id not in polygons:
            # this polygon was already combined with another
            continue

        p = polygons[poly_id]
        poly = p["polygon"]
        buffered_poly = poly.buffer(0.00001)
        # get the neighbors of the polygon from the rtree
        neighbors = list(idx.intersection(poly.envelope.bounds, objects=True))
        neighbors = [n.object for n in neighbors if n.object["id"] != poly_id]

        # combine the polygon with any neighbor that has the same name OR has no name and is touching
        for neighbor in neighbors:
            neighbor_poly = neighbor["polygon"]
            if (
                (
                    "glac_name" in neighbor["properties"]
                    and "glac_name" in p["properties"]
                )
                and neighbor["properties"]["glac_name"] == p["properties"]["glac_name"]
                and neighbor_poly.intersects(buffered_poly)
            ) or (
                "glac_name" not in neighbor["properties"]
                and neighbor_poly.intersects(buffered_poly)
            ):
                combined_poly = poly.union(neighbor_poly)
                # remove the neighbor and current polygon from the rtree
                idx.delete(neighbor["id"], neighbor_poly.envelope.bounds)
                idx.delete(poly_id, poly.envelope.bounds)

                del polygons[poly_id]
                del polygons[neighbor["id"]]

                # add a new polygon to the tree with the combined polygon
                new_poly_id = uuid.uuid4().int
                unchecked_ids.append(new_poly_id)
                polygons[new_poly_id] = {
                    "polygon": combined_poly,
                    "id": new_poly_id,
                    "properties": p["properties"],
                }
                idx.insert(
                    new_poly_id,
                    combined_poly.envelope.bounds,
                    obj={
                        "polygon": combined_poly,
                        "id": new_poly_id,
                        "properties": polygon["properties"],
                    },
                )
                break

    new_polygons = []
    for poly_id in polygons:
        poly = polygons[poly_id]["polygon"]
        properties = polygons[poly_id]["properties"]

        # check if the polygon is simple
        if not poly.is_simple or not poly.is_valid:
            print("Polygon is not simple or valid, attempting to fix...")
            # if not, make it simple
            poly = poly.buffer(0)
            if not poly.is_simple or not poly.is_valid:
                raise Exception("Failed to make polygon simple and valid")

        new_polygons.append(
            geojson.Feature(
                geometry=poly.__geo_interface__,
                properties=properties,
            )
        )

    gj["features"] = new_polygons

    # save the polygons to a new geojson
    with open(cleaned_glaciers_output_file, "w") as f:
        geojson.dump(gj, f)

    print("Creating simplified glacier boundaries...")
    simplify_geojson_geometries(
        "data/temp/combined-glaciers.geojson",
        "data/temp/simplified-glaciers.geojson",
        pre_simplify_tolerance,
    )
    print("Creating medial axes from simplified boundaries...")
    weighted_medial_axes_from_geojson(
        "data/temp/simplified-glaciers.geojson",
        "data/temp/weighted-medial-axes.geojson",
        multiprocessing.cpu_count(),
    )
    print("Simplifying medial axes...")
    simplify_geojson_geometries(
        "data/temp/weighted-medial-axes.geojson",
        labels_output_file,
        medial_axes_tolerance,
    )


if __name__ == "__main__":
    cli()
