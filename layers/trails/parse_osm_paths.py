import osmium
import click
import os
import fiona
import json

from shapely.geometry import LineString, mapping


class OSMPathHandler(osmium.SimpleHandler):
    def __init__(self):
        super(OSMPathHandler, self).__init__()
        self.paths = []
        self.tags = []

    def way(self, w):
        sequence = []
        for n in w.nodes:
            if n.location.valid():
                sequence.append((n.location.lon, n.location.lat))
        if len(sequence) > 1:
            self.tags.append({tag.k: tag.v for tag in w.tags})
            self.paths.append(
                (
                    LineString(sequence),
                    {
                        "id": w.id,
                        "ref": w.tags["ref"]
                        if "ref" in w.tags
                        else None,  # TODO: extract from trail name if ref is null and name has a number
                        "name": w.tags["name"]
                        if "name" in w.tags
                        else None,  # TODO: replace "Number" with #
                        "bridge": w.tags["bridge"] == "yes"
                        if "bridge" in w.tags
                        else None,
                        "bicycle": w.tags["bicycle"] == "yes"
                        or w.tags["bicycle"] == "designated"
                        if "bicycle" in w.tags
                        else None,
                        "horse": w.tags["horse"] or w.tags["horse"] == "designated"
                        if "horse" in w.tags
                        else None,
                        "dog": w.tags["dog"] if "dog" in w.tags else None,
                        "surface": w.tags["surface"] if "surface" in w.tags else None,
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
    help="The output geopackage for path lines",
    default="data/temp/osm_paths.gpkg",
)
def cli(input_file, output_file):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Parsing osm data and creating paths...")
    osm_handler = OSMPathHandler()
    osm_handler.apply_file(
        input_file, locations=True, idx="flex_mem"
    )  # use idx=dense_mmap_array for large files on linux

    # save tags as json
    print("Saving tags...")
    with open("data/temp/osm_paths_tags.json", "w") as f:
        f.write(json.dumps(osm_handler.tags))

    print("Saving paths...")
    trail_schema = {
        "geometry": "LineString",
        "properties": {
            "id": "int",
            "ref": "str",
            "name": "str",
            "surface": "str",
            "bridge": "bool",
            "bicycle": "bool",
            "horse": "bool",
            "dog": "bool",
            "snowmobile": "bool",
            "snowshoe": "bool",
            "xcski": "bool",
            "groomed": "bool",
        },
    }
    with fiona.open(
        output_file, "w", driver="GPKG", crs="EPSG:4326", schema=trail_schema
    ) as output:
        for path in osm_handler.paths:
            output.write(
                {
                    "geometry": mapping(path[0]),
                    "properties": {
                        "id": path[1]["id"],
                        "ref": path[1]["ref"],
                        "name": path[1]["name"],
                        "surface": path[1]["surface"],
                        "bridge": path[1]["bridge"],
                        "bicycle": path[1]["bicycle"],
                        "horse": path[1]["horse"],
                        "dog": path[1]["dog"],
                        "snowmobile": None,
                        "snowshoe": None,
                        "xcski": None,
                        "groomed": None,
                    },
                }
            )


if __name__ == "__main__":
    cli()
