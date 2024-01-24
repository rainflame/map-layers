import click
import rasterio


@click.command()
@click.option(
    "--input-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The input .tif file",
    default="data/sources/input.tif",
)
@click.option(
    "--output-file",
    type=click.Path(file_okay=True, dir_okay=False),
    help="The output .tif file",
    default="data/temp/cleaned.tif",
)
@click.option(
    "--filter-values",
    type=click.STRING,
    required=True,
    help="Comma separated list of pixel values to filter out",
)
def cli(input_file, output_file, filter_values):
    # split the filter values
    filter_values = filter_values.split(",")
    filter_values = [int(x) for x in filter_values]

    # load the input file with rasterio
    with rasterio.open(input_file) as src:
        print(f"Setting pixel values {filter_values} to {src.nodata}...")
        # filter out the values
        data = src.read(1)
        for value in filter_values:
            data[data == value] = src.nodata

        # write the output file
        print("Writing output file...")
        profile = src.profile
        with rasterio.open(output_file, "w", **profile) as dst:
            dst.write(data, 1)


if __name__ == "__main__":
    cli()
