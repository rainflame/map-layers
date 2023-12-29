import fiona
import click
import uuid

from rtree import index
from tqdm import tqdm
from fiona import Properties
from shapely.geometry import Point, mapping
from geopy.distance import distance


@click.command()
@click.option(
    "--bbox",
    default="-122.04976264563147,43.51921441989123,-120.94591116755655,44.39466349563759",
    help="Bounding box to trim the prominence data",
)
@click.option(
    "--input-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The input .gpkg points file",
    default="data/temp/pois_natural.gpkg",
)
@click.option(
    "--prominence-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The txt file containing the prominence data",
    default="data/sources/all-peaks-sorted-p100.txt",
)
@click.option(
    "--output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output geopackage for natural points of interest with prominence data",
    default="data/temp/peaks_prominence.gpkg",
)
@click.option(
    "--to-feet",
    is_flag=True,
    help="Convert the elevation from meters to feet",
    default=False,
)
def cli(bbox, input_file, prominence_file, output_file, to_feet):
    xmin, ymin, xmax, ymax = [float(x) for x in bbox.split(",")]
    idx = index.Index()
    peaks = 0

    print("Loading prominence data...")
    with open(prominence_file, "r") as f:
        for line in tqdm(f):
            # latitude,longitude,elevation,key saddle latitude,key saddle longitude,prominence in meters
            prominence_data = line.strip().split(",")
            # if the point is outside the bbox, skip it
            if (
                float(prominence_data[1]) < xmin
                or float(prominence_data[1]) > xmax
                or float(prominence_data[0]) < ymin
                or float(prominence_data[0]) > ymax
            ):
                continue

            prominence = float(prominence_data[5])
            if to_feet:
                prominence = prominence * 3.28084

            coords = (float(prominence_data[1]), float(prominence_data[0]))
            idx.insert(
                id=uuid.uuid4().int,
                coordinates=coords,
                obj={
                    "prominence": prominence,
                    "coords": coords,
                },
            )
            peaks += 1

    print(f"Loaded {peaks} peaks")

    features = 0
    matches = 0
    peak_data = []

    print("Associating prominence data with points...")
    with fiona.open(input_file, "r") as source:
        new_schema = source.schema.copy()

        # iterate through each feature in the input file
        for feature in tqdm(source):
            features += 1
            # get the coordinates of the feature
            coords = feature["geometry"]["coordinates"]
            coords = (coords[0], coords[1])

            # find the closest prominence data point
            closest = list(idx.nearest(coords, 1, objects=True))[0]
            dist = distance(
                (coords[1], coords[0]),
                (closest.object["coords"][1], closest.object["coords"][0]),
            ).meters
            if dist < 100:
                prominence_data = closest.object
                this_peak = {"feature": feature, "prominence_data": prominence_data}
                peak_data.append(this_peak)
                matches += 1
            else:
                # we didn't find a match in the prominence data, so mark it as 0
                this_peak = {
                    "feature": feature,
                    "prominence_data": {
                        "prominence": 0,
                    },
                }
                peak_data.append(this_peak)

    print(f"Matched {matches} of {features} peaks")

    peak_data.sort(key=lambda peak: peak["prominence_data"]["prominence"], reverse=True)
    # get the top 5% of peaks by prominence
    highest_promienence_index = int(len(peak_data) * 0.05)
    # get the next 15%
    mid_prominence_index = highest_promienence_index + int(len(peak_data) * 0.15)

    for i, peak in enumerate(peak_data):
        if i < highest_promienence_index:
            peak["prominence_data"]["rel_prominence"] = 1
        elif i < mid_prominence_index:
            peak["prominence_data"]["rel_prominence"] = 2
        else:
            peak["prominence_data"]["rel_prominence"] = 3

    # create a new output file
    new_schema["properties"]["prominence"] = "int"
    new_schema["properties"]["rel_prominence"] = "int"

    output_files = [output_file.replace(".gpkg", f"_{i}.gpkg") for i in range(1, 4)]
    for i, file in enumerate(output_files):
        with fiona.open(
            file,
            "w",
            driver="GPKG",
            schema=new_schema,
            crs=source.crs,
            encoding="utf-8",
        ) as dst:
            filtered_peak_data = [
                peak
                for peak in peak_data
                if peak["prominence_data"]["rel_prominence"] == i + 1
            ]
            for feature in filtered_peak_data:
                props = Properties(
                    **feature["feature"]["properties"],
                    prominence=feature["prominence_data"]["prominence"],
                    rel_prominence=feature["prominence_data"]["rel_prominence"],
                )
                dst.write(
                    {"geometry": feature["feature"]["geometry"], "properties": props}
                )


if __name__ == "__main__":
    cli()
