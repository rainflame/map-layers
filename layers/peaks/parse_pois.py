import osmium
import click
import os
import fiona

from shapely.geometry import Point, mapping


class OSMPoiHandler(osmium.SimpleHandler):
    def __init__(self):
        super(OSMPoiHandler, self).__init__()
        self.peaks = []

    def is_peak(self, w):
        return "natural" in w.tags and w.tags["natural"] == "peak"

    def is_volcano(self, w):
        return "natural" in w.tags and w.tags["natural"] == "volcano"

    def is_hill(self, w):
        return "natural" in w.tags and w.tags["natural"] == "hill"

    def node(self, a):
        if self.is_peak(a) or self.is_volcano(a) or self.is_hill(a):
            self.peaks.append(
                (
                    Point(a.location.lon, a.location.lat),
                    {
                        "name": a.tags["name"] if "name" in a.tags else None,
                        "peak": a.tags["natural"] == "peak"
                        if "natural" in a.tags
                        else False,
                        "volcano": a.tags["natural"] == "volcano"
                        if "natural" in a.tags
                        else False,
                        "hill": a.tags["natural"] == "hill"
                        if "natural" in a.tags
                        else False,
                        "ele": float(a.tags["ele"]) if "ele" in a.tags else None,
                        "wikipedia": a.tags["wikipedia"]
                        if "wikipedia" in a.tags
                        else None,
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
    "--output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for natural points of interest",
    default="data/temp/pois_natural.gpkg",
)
@click.option(
    "--to-feet",
    is_flag=True,
    help="Convert the elevation from meters to feet",
    default=False,
)
def cli(input_file, output_file, to_feet):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Parsing osm data and creating points of interest...")
    osm_handler = OSMPoiHandler()
    osm_handler.apply_file(
        input_file, locations=True, idx="flex_mem"
    )  # use idx=dense_mmap_array for large files on linux

    print("Saving points of interest...")
    schema = {
        "geometry": "Point",
        "properties": {
            "name": "str",
            "peak": "bool",
            "volcano": "bool",
            "hill": "bool",
            "ele": "int",
            "wikipedia": "str",
        },
    }
    with fiona.open(
        output_file, "w", driver="GPKG", crs="EPSG:4326", schema=schema
    ) as output:
        for peak in osm_handler.peaks:
            data = {"geometry": mapping(peak[0]), "properties": peak[1]}
            if to_feet and data["properties"]["ele"] is not None:
                data["properties"]["ele"] = round(data["properties"]["ele"] * 3.28084)
            output.write(data)


if __name__ == "__main__":
    cli()
