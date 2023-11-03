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

from polygons_to_weighted_medial_axes import get_weighted_medial_axis
from simplify import simplify_geometry


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
@click.option(
    "--workers",
    default=multiprocessing.cpu_count(),
    help="Number of workers to use",
)
def cli(
    input_file,
    cleaned_glaciers_output_file,
    labels_output_file,
    pre_simplify_tolerance,
    medial_axes_tolerance,
    workers,
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

    combined_glacier_polygons = []
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

        combined_glacier_polygons.append((poly, properties))

    print("Creating simplified glacier boundaries...")

    simplified_glaciers = []
    for poly, properties in tqdm(combined_glacier_polygons):
        simplified_polygon = simplify_geometry(poly, pre_simplify_tolerance)
        simplified_glaciers.append((simplified_polygon, properties))

    print("Creating medial axes from simplified boundaries...")

    medial_axes = []
    with multiprocessing.Pool(workers) as p:
        for line, properties in tqdm(
            p.imap_unordered(get_weighted_medial_axis, simplified_glaciers),
            total=len(simplified_glaciers),
        ):
            if line is None:
                continue
            medial_axes.append((line, properties))

    print("Simplifying medial axes...")

    simplified_medial_axes = []
    for line, properties in tqdm(medial_axes):
        simplified_line = simplify_geometry(line, medial_axes_tolerance)
        simplified_medial_axes.append((simplified_line, properties))

    # save the simplified medial axes
    with open(labels_output_file, "w") as f:
        gj = geojson.FeatureCollection(
            [
                geojson.Feature(geometry=line, properties=properties)
                for line, properties in simplified_medial_axes
            ],
            crs=gj["crs"],
        )
        geojson.dump(gj, f)

    # save the combined glacier polygons
    with open(cleaned_glaciers_output_file, "w") as f:
        gj = geojson.FeatureCollection(
            [
                geojson.Feature(geometry=poly, properties=properties)
                for poly, properties in combined_glacier_polygons
            ],
            crs=gj["crs"],
        )
        geojson.dump(gj, f)


if __name__ == "__main__":
    cli()
