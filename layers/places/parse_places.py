import osmium
import click
import os
import fiona

from shapely.geometry import Point, MultiPolygon, Polygon, mapping, shape
import shapely.wkb as wkblib

wkbfab = osmium.geom.WKBFactory()


# https://wiki.openstreetmap.org/wiki/Key:place
class OSMPlaceHandler(osmium.SimpleHandler):
    def __init__(self):
        super(OSMPlaceHandler, self).__init__()
        self.points_prominence_1 = []
        self.points_prominence_2 = []
        self.points_prominence_3 = []
        self.polys = []

    def is_reservation(self, w):
        return "boundary" in w.tags and w.tags["boundary"] == "aboriginal_lands"

    def is_area(self, w):
        return (
            "boundary" in w.tags
            and w.tags["boundary"] in ["protected_area", "national_park"]
        ) or (
            "leisure" in w.tags
            and w.tags["leisure"] in ["nature_reserve", "park", "dog_park"]
        )

    def is_place(self, w):
        return "place" in w.tags and w.tags["place"] in [
            "city",
            "town",
            "village",
            "hamlet",
            "suburb",
            "locality",
            "island",
            "islet",
            "farm",
            "isolated_dwelling",
            "neighbourhood",
        ]

    def is_place_prominence1(self, w):
        return "place" in w.tags and w.tags["place"] in [
            "city",
        ]

    def is_place_prominence2(self, w):
        return "place" in w.tags and w.tags["place"] in [
            "town",
            "village",
        ]

    def is_place_prominence3(self, w):
        return "place" in w.tags and w.tags["place"] in [
            "hamlet",
            "suburb",
            "locality",
            "island",
            "islet",
            "farm",
            "isolated_dwelling",
            "neighbourhood",
        ]

    def node(self, n):
        if self.is_place(n):
            point_data = (
                Point(n.location.lon, n.location.lat),
                {
                    "id": n.id,
                    "name": n.tags["name"] if "name" in n.tags else None,
                    "type": n.tags["place"],
                },
            )

            if self.is_place_prominence1(n):
                self.points_prominence_1.append(point_data)
            elif self.is_place_prominence2(n):
                self.points_prominence_2.append(point_data)
            elif self.is_place_prominence3(n):
                self.points_prominence_3.append(point_data)

    def area(self, a):
        if self.is_reservation(a) or self.is_area(a):
            wkb = wkbfab.create_multipolygon(a)
            poly = wkblib.loads(wkb, hex=True)

            if self.is_reservation(a):
                self.polys.append(
                    (
                        poly,
                        {
                            "id": a.id,
                            "name": a.tags["name"] if "name" in a.tags else None,
                            "type": "reservation",
                            "operator": None,
                            "protection_title": None,
                        },
                    )
                )

            if self.is_area(a):
                self.polys.append(
                    (
                        poly,
                        {
                            "id": a.id,
                            "name": a.tags["name"] if "name" in a.tags else None,
                            "type": (
                                a.tags["boundary"]
                                if "boundary" in a.tags
                                else a.tags["leisure"] if "leisure" in a.tags else None
                            ),
                            "operator": (
                                a.tags["operator"] if "operator" in a.tags else None
                            ),
                            "protection_title": (
                                a.tags["protection_title"]
                                if "protection_title" in a.tags
                                else None
                            ),
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
    "--blm-input-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The input geopackage containing BLM boundaries",
    default="data/temp/BLM.gpkg",
)
@click.option(
    "--polygon-output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for place polygons",
    default="data/temp/place-polygons.gpkg",
)
@click.option(
    "--point-output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for place points",
    default="data/temp/place-points.gpkg",
)
def cli(input_file, blm_input_file, polygon_output_file, point_output_file):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(polygon_output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_dir = os.path.dirname(point_output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Parsing BLM boundaries...")
    # open the blm geopacakge
    blm_polys = []
    with fiona.open(blm_input_file) as src:
        for feature in src:
            poly = MultiPolygon(shape(feature["geometry"]))
            blm_polys.append(
                (
                    poly,
                    {
                        "id": feature["id"],
                        "name": "BLM",  # could use the field office name here
                        "type": "protected_area",
                        "operator": "Beureau of Land Management",
                        "protection_title": None,
                    },
                )
            )

    print("Parsing osm data and creating places...")
    osm_handler = OSMPlaceHandler()
    osm_handler.apply_file(
        input_file, locations=True, idx="flex_mem"
    )  # use idx=dense_mmap_array for large files on linux

    print("Saving places...")
    schema = {
        "geometry": "MultiPolygon",
        "properties": {
            "id": "int",
            "name": "str",
            "type": "str",
            "operator": "str",
            "protection_title": "str",
        },
    }
    with fiona.open(
        polygon_output_file, "w", driver="GPKG", crs="EPSG:4326", schema=schema
    ) as output:
        for poly in osm_handler.polys:
            output.write(
                {
                    "geometry": mapping(poly[0]),
                    "properties": {
                        "id": poly[1]["id"],
                        "name": poly[1]["name"],
                        "type": poly[1]["type"],
                        "operator": poly[1]["operator"],
                        "protection_title": poly[1]["protection_title"],
                    },
                }
            )

        for poly in blm_polys:
            output.write(
                {
                    "geometry": mapping(poly[0]),
                    "properties": {
                        "id": poly[1]["id"],
                        "name": poly[1]["name"],
                        "type": poly[1]["type"],
                        "operator": poly[1]["operator"],
                        "protection_title": poly[1]["protection_title"],
                    },
                }
            )

    schema = {
        "geometry": "Point",
        "properties": {
            "id": "int",
            "name": "str",
            "type": "str",
        },
    }

    for point_list, prominence in [
        (osm_handler.points_prominence_1, 1),
        (osm_handler.points_prominence_2, 2),
        (osm_handler.points_prominence_3, 3),
    ]:
        print(f"Saving places with prominence {prominence}...")
        file = point_output_file.replace(".gpkg", f"-prominence-{prominence}.gpkg")
        with fiona.open(
            file, "w", driver="GPKG", crs="EPSG:4326", schema=schema
        ) as output:
            for point in point_list:
                output.write(
                    {
                        "geometry": mapping(point[0]),
                        "properties": {
                            "id": point[1]["id"],
                            "name": point[1]["name"],
                            "type": point[1]["type"],
                        },
                    }
                )


if __name__ == "__main__":
    cli()
