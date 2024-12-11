import tqdm
import glob
import rasterio
import click
from rasterio.warp import calculate_default_transform, reproject, Resampling


@click.command()
# @click.option(
#     "--workers", default=multiprocessing.cpu_count(), help="Number of workers to use"
# )
@click.option(
    "--input-files", default="data/sources/*tif", help="Input files to reproject"
)
@click.option("--crs", default="EPSG:4326", help="CRS to reproject the rasters to")
@click.option(
    "--nodata-value", default="-999999", help="Value to set for nodata pixels"
)
def cli(input_files, crs, nodata_value):

    files = glob.glob(input_files)

    print("Setting nodata values to {}".format(nodata_value))
    for file_path in tqdm.tqdm(files):
        with rasterio.open(file_path) as src:
            profile = src.profile
            profile.update(nodata=nodata_value)

            # replace nodata value
            data = src.read()
            data[data == src.nodata] = nodata_value

            with rasterio.open(file_path, "w", **profile) as dst:
                dst.write(data)

    print(f"Converting rasters to {crs}...")
    for file_path in tqdm.tqdm(files):
        with rasterio.open(file_path) as src:

            transform, width, height = calculate_default_transform(
                src.crs, crs, src.width, src.height, *src.bounds
            )

            kwargs = src.meta.copy()
            kwargs.update(
                {
                    "crs": crs,
                    "transform": transform,
                    "width": width,
                    "height": height,
                }
            )

            with rasterio.open(file_path, "w", **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=crs,
                        resampling=Resampling.nearest,
                    )


if __name__ == "__main__":
    cli()
