import osmium
import click
import os
import fiona

from shapely.geometry import Point, LineString, MultiPolygon, Polygon, mapping


# https://wiki.openstreetmap.org/wiki/Key:waterway
class OSMWaterwayHandler(osmium.SimpleHandler):
    def __init__(self):
        super(OSMWaterwayHandler, self).__init__()
        self.water = []
        self.waterways = []

    def is_water(self, w):
        return ("natural" in w.tags and w.tags["natural"] == "water") or (
            "water" in w.tags
            and w.tags["water"]
            in [
                "lake",
                "reservoir",
                "pond",
                "river",
                "stream",
                "oxbow",
                "canal",
                "drain",
                "ditch",
            ]
        )

    def is_waterway(self, w):
        return "waterway" in w.tags and w.tags["waterway"] in [
            "river",
            "stream",
            "canal",
            "drain",
            "ditch",
        ]

    def way(self, w):
        if self.is_waterway(w):
            sequence = []
            for n in w.nodes:
                if n.location.valid():
                    sequence.append((n.location.lon, n.location.lat))
            if len(sequence) > 1:
                self.waterways.append(
                    (
                        LineString(sequence),
                        {
                            "id": w.id,
                            "name": w.tags["name"] if "name" in w.tags else None,
                            "type": w.tags["waterway"]
                            if "waterway" in w.tags
                            else None,
                            "intermittent": w.tags["intermittent"]
                            if "intermittent" in w.tags
                            else None,
                        },
                    )
                )

    def area(self, a):
        if self.is_water(a):
            poly_sequence = []
            for outer in a.outer_rings():
                outer_ring = Polygon(
                    [
                        Point(n.location.lon, n.location.lat)
                        for n in outer
                        if n.location.valid()
                    ]
                )
                inner_rings = []
                for ring in a.inner_rings(outer):
                    inner_rings.append(
                        Polygon(
                            [
                                Point(n.location.lon, n.location.lat)
                                for n in ring
                                if n.location.valid()
                            ]
                        )
                    )
                poly_sequence.append((outer_ring, inner_rings))

            poly = MultiPolygon(poly_sequence)
            self.water.append(
                (
                    poly,
                    {
                        "id": a.id,
                        "name": a.tags["name"] if "name" in a.tags else None,
                        "type": a.tags["water"] if "water" in a.tags else None,
                    },
                )
            )


@click.command()
@click.option(
    "--input-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The input .osm.pbf file",
    default="data/sources/extract.osm.pbf",
)
@click.option(
    "--lake-output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for water polygons",
    default="data/temp/water.gpkg",
)
@click.option(
    "--river-output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for waterway lines",
    default="data/temp/waterways.gpkg",
)
def cli(input_file, lake_output_file, river_output_file):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(lake_output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = os.path.dirname(river_output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Parsing osm data and creating water/waterways...")
    osm_handler = OSMWaterwayHandler()
    osm_handler.apply_file(
        input_file, locations=True, idx="flex_mem"
    )  # use idx=dense_mmap_array for large files on linux

    print("Saving water...")
    schema = {
        "geometry": "MultiPolygon",
        "properties": {"id": "int", "name": "str", "type": "str"},
    }
    with fiona.open(
        lake_output_file, "w", driver="GPKG", crs="EPSG:4326", schema=schema
    ) as output:
        for water in osm_handler.water:
            # print(water[1])
            output.write(
                {
                    "geometry": mapping(water[0]),
                    "properties": {
                        "id": water[1]["id"],
                        "name": water[1]["name"],
                        "type": water[1]["type"],
                    },
                }
            )

    print("Saving waterways...")
    schema = {
        "geometry": "LineString",
        "properties": {
            "id": "int",
            "name": "str",
            "type": "str",
            "intermittent": "str",
        },
    }
    with fiona.open(
        river_output_file, "w", driver="GPKG", crs="EPSG:4326", schema=schema
    ) as output:
        for river in osm_handler.waterways:
            output.write(
                {
                    "geometry": mapping(river[0]),
                    "properties": {
                        "id": river[1]["id"],
                        "name": river[1]["name"],
                        "type": river[1]["type"],
                        "intermittent": river[1]["intermittent"],
                    },
                }
            )


if __name__ == "__main__":
    cli()
