import fiona
import click
import os
import uuid
import jellyfish

from rtree import index
from tqdm import tqdm
from shapely.geometry import shape, MultiPolygon, mapping


@click.command()
@click.option(
    "--input-file",
    help="The input geopackage",
    default="data/temp/wildfires.gpkg",
)
@click.option(
    "--output-file",
    help="The output geopackage",
    default="data/temp/wildfires-dedupped.gpkg",
)
def cli(input_file, output_file):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    idx = index.Index()
    polygons = {}

    # Load the dataset
    print("Loading the dataset...")
    with fiona.open(input_file, "r") as features:
        for feature in tqdm(features):
            poly = shape(feature["geometry"])
            new_id = uuid.uuid4().int
            polygons[new_id] = {
                "polygon": poly,
                "id": new_id,
                "properties": feature["properties"],
                "duplicate": False,
            }

            # load each feature into the rtree
            idx.insert(
                new_id,
                poly.envelope.bounds,
                obj=polygons[new_id],
            )

    print("finding duplicated wildfires...")
    for poly_id in tqdm(polygons):
        if polygons[poly_id]["duplicate"]:
            # skip polygons that have already been removed
            continue

        # get any intersecting polygons
        intersecting_polygons = list(
            idx.intersection(polygons[poly_id]["polygon"].bounds, objects=True)
        )
        intersecting_polygons = [
            n.object for n in intersecting_polygons if n.object["id"] != poly_id
        ]

        for intersecting_poly in intersecting_polygons:
            if polygons[intersecting_poly["id"]]["duplicate"]:
                # skip polygons that have already been removed
                continue

            if (
                polygons[poly_id]["properties"]["year"]
                != intersecting_poly["properties"]["year"]
            ):
                # never consider polygons from different years to be duplicates
                continue

            if (
                jellyfish.jaro_winkler_similarity(
                    polygons[poly_id]["properties"]["name"],
                    intersecting_poly["properties"]["name"],
                )
                < 0.5
            ):
                # skip polygons with names that are too dissimilar
                continue

            area1 = polygons[poly_id]["polygon"].area
            area2 = intersecting_poly["polygon"].area

            area_percent_diff = abs(area1 - area2) / ((area1 + area2) / 2)
            if area_percent_diff > 0.2:
                # skip polygons that are too different in size
                continue

            intersection = polygons[poly_id]["polygon"].intersection(
                intersecting_poly["polygon"]
            )
            # is the intersection less than 80% of the area of both polygons?
            if intersection.area < (area1 * 0.8) and intersection.area < (area2 * 0.8):
                continue

            # now we can be pretty sure we've found a duplicate
            # merge the two polygons
            combined_poly = polygons[poly_id]["polygon"].union(
                intersecting_poly["polygon"]
            )

            # if its a polygon, create a multipolygon
            if combined_poly.geom_type == "Polygon":
                combined_poly = MultiPolygon([combined_poly])

            # merge the two properties
            combined_properties = polygons[poly_id]["properties"]
            combined_properties.update(intersecting_poly["properties"])

            # update the current poly with combined values and poly
            polygons[poly_id]["polygon"] = combined_poly
            polygons[poly_id]["properties"] = combined_properties

            # remove the intersecting poly from the rtree
            idx.delete(intersecting_poly["id"], intersecting_poly["polygon"].bounds)
            polygons[intersecting_poly["id"]]["duplicate"] = True

    # save the output
    print("Saving the output...")

    schema = {
        "geometry": "MultiPolygon",
        "properties": {
            "name": "str",
            "year": "int",
            "agency": "str",
            "cause1": "str",
            "cause2": "str",
            "cause3": "str",
            "startdate": "str",
            "enddate": "str",
            "source": "str",
        },
    }

    with fiona.open(
        output_file, "w", driver="GPKG", crs="EPSG:4326", schema=schema
    ) as output:
        for poly_id in tqdm(polygons):
            if polygons[poly_id]["duplicate"]:
                # skip polygons that have already been removed
                continue

            output.write(
                {
                    "geometry": mapping(polygons[poly_id]["polygon"]),
                    "properties": polygons[poly_id]["properties"],
                }
            )


if __name__ == "__main__":
    cli()
