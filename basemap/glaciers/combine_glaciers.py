import click
import uuid

from shapely.geometry import Polygon
from rtree import index

import fiona


@click.command()
@click.option(
    "--input-file",
    help="The input glaciers geopackage",
    default="data/temp/glaciers-filtered.gpkg",
)
@click.option(
    "--output-file",
    help="The output geopackage",
    default="data/output/glaciers.gpkg",
)
def cli(
    input_file,
    output_file,
):
    # load the input file
    with fiona.open(input_file) as src:
        polygons = {}
        # load the polygons into an rtree
        idx = index.Index()
        for feature in src:
            # get feature geometry
            geom = feature["geometry"]
            poly = Polygon(geom["coordinates"][0])
            new_id = uuid.uuid4().int
            polygons[new_id] = {
                "polygon": poly,
                "id": new_id,
                "properties": feature["properties"],
            }
            idx.insert(
                new_id,
                poly.envelope.bounds,
                obj=polygons[new_id],
            )

        unchecked_ids = [poly_id for poly_id in polygons]

        print("Combining touching glaciers with the same name or no name...")
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
                    neighbor["properties"]["glac_name"] == p["properties"]["glac_name"]
                    and neighbor_poly.intersects(buffered_poly)
                ) or (
                    neighbor["properties"]["glac_name"] == "None"
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
                            "properties": p["properties"],
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

        # write the combined polygons to a new geopackage
        print(f"Saving {len(combined_glacier_polygons)} glaciers...")
        with fiona.open(
            output_file,
            "w",
            driver="GPKG",
            crs=src.crs,
            schema=src.schema,
        ) as dst:
            for poly, properties in combined_glacier_polygons:
                dst.write(
                    {
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [list(poly.exterior.coords)],
                        },
                        "properties": properties,
                    }
                )


if __name__ == "__main__":
    cli()
