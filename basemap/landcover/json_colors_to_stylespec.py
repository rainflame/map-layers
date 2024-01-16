import click
import glob
import os
import pandas as pd
import fiona
import json

from tqdm import tqdm


@click.command()
@click.option(
    "--input-file",
    default="data/output/classes.json",
    help="The JSON file with landcover colors",
)
@click.option(
    "--output-file",
    default="data/output/stylespec.json",
    help="Output Maplibre-GL stylespec file",
)
def cli(input_file, output_file):
    inputs = glob.glob(input_file)
    if len(inputs) >= 1:
        input_file = inputs[0]
    else:
        raise ValueError(f"Input file does not exist: {input_file}")
    pass

    # verify the path ot the output file exists, if not create it
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # read the input json file
    with open(input_file, "r") as f:
        data = json.load(f)

    spec = ["match", ["get", "class"]]

    for key in data.keys():
        spec.append(float(key))
        spec.append(data[key]["color"])

    # save the output file as json
    with open(output_file, "w") as f:
        json.dump(spec, f)


if __name__ == "__main__":
    cli()
