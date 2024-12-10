import click
import multiprocessing
import rio_rgbify.mbtiler as mbtiler
from rasterio.warp import transform_bounds


def fixed_transform_bounds(*args, **kwargs):
    if "densify_pts" in kwargs:
        kwargs["densify_pts"] = 2
    return transform_bounds(*args, **kwargs)


mbtiler.transform_bounds = fixed_transform_bounds


# click cli to get number of workers and bounding box
@click.command()
@click.option(
    "--workers", default=multiprocessing.cpu_count(), help="Number of workers to use"
)
@click.option("--input-dataset", help="Dataset to convert")
@click.option("--output-mbtiles", help="Output mbtiles file")
@click.option("--min-z", default=1)
@click.option("--max-z", default=14)
def cli(workers, input_dataset, output_mbtiles, min_z, max_z):
    print("Running with", workers, "workers")
    print("Converting", input_dataset, "to", output_mbtiles)
    with mbtiler.RGBTiler(
        input_dataset,
        output_mbtiles,
        interval=0.1,
        base_val=-10000,
        format="webp",
        max_z=max_z,
        min_z=min_z,
    ) as tiler:
        tiler.run(workers)


if __name__ == "__main__":
    cli()
