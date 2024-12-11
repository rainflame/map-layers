import rasterio
import glob
from shapely import Polygon
import rasterio.merge
import tqdm
import numpy as np
import math
import multiprocessing

# merge all tif rasters in data/sources

import rasterio
from rasterio.windows import Window
from rasterio.merge import merge

# Input VRT and output raster file paths
vrt_path = "data/temp/dem.vrt"
output_raster_path = "data/temp/mosaic_output.tif"

# Open the VRT
with rasterio.open(vrt_path) as vrt:
    # Copy metadata from the VRT
    out_meta = vrt.meta.copy()

    width = vrt.width
    height = vrt.height

    # Get block size (tile size) for band 1
    block_width, block_height = vrt.block_shapes[0]  # First band's block size

    # Calculate total windows
    num_windows_x = math.ceil(width / block_width)
    num_windows_y = math.ceil(height / block_height)
    total_windows = num_windows_x * num_windows_y

    print(f"Total windows: {total_windows}")
    print(f"Block size: {block_width}x{block_height}")

    # Update metadata for the output file
    out_meta.update(
        {
            "driver": "GTiff",
            "dtype": "float32",  # Change if needed
            "compress": "lzw",  # Optional compression
        }
    )

    # Process data in chunks
    windows = vrt.block_windows(1)

    def process_windows(window):
        data_samples = []
        with rasterio.open(vrt_path) as vrt:
            # get pixels from each raster in the vrt for this window
            for raster in vrt.files:
                with rasterio.open(raster) as src:
                    # masked to read as a numpy masked array
                    data = src.read(window=window, masked=True)
                    # if the data is not 128x128, pad it with masked values
                    if data.shape != (1, 128, 128):
                        padded_data = np.ma.masked_all((1, 128, 128))
                        padded_data[
                            :,
                            : data.shape[1],
                            : data.shape[2],
                        ] = data
                        data = padded_data
                    data_samples.append(data)

            # discard any samples that are completely masked
            data_samples = [data for data in data_samples if not data.mask.all()]

            merged_array = data_samples[0].copy()

            for array in data_samples[1:]:
                # Fill masked values in the current merged array with values from the next array
                merged_array = np.ma.array(
                    np.where(
                        merged_array.mask, array, merged_array
                    ),  # Fill masked values
                    mask=(merged_array.mask & array.mask),  # Combine masks
                )

            with rasterio.open(output_raster_path, "w", **out_meta) as dest:
                # Write the data to the output raster
                dest.write(merged_array, window=window)

    with multiprocessing.Pool(processes=10) as pool:
        for _ in tqdm.tqdm(
            pool.imap_unordered(process_windows, windows), total=total_windows
        ):
            pass
        pool.close()
        pool.join()


# files = glob.glob("data/sources/*.tif")

# image_bounds = []

# for file in files:
#     with rasterio.open(file) as src:
#         bounds = []
#         # create a polygon from the bounds of the raster
#         top_left = [src.bounds.left, src.bounds.top]
#         top_right = [src.bounds.right, src.bounds.top]
#         bottom_left = [src.bounds.left, src.bounds.bottom]
#         bottom_right = [src.bounds.right, src.bounds.bottom]
#         bounds.append(
#             Polygon([top_left, top_right, bottom_right, bottom_left, top_left])
#         )
#         image_bounds.append((file, bounds))

# for file, bounds in image_bounds:
#     # check if the bounds overlap with the bounds of the other rasters
#     for other_file, other_bounds in image_bounds:
#         if file == other_file:
#             continue
#         if bounds[0].intersects(other_bounds[0]):
#             print(f"{file} intersects with {other_file}")

# print("merging {} files...".format(len(files)))
# new_file = rasterio.merge.merge(files)

# print("saving file")
# # save the new file to data/temp/merged.tif
# with rasterio.open("data/temp/merged.tif", "w", **new_file[0].meta) as dst:
#     for f in new_file:
#         dst.write(f.read(1), 1)
