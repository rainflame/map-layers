import rasterio
import click 
import numpy as np 
from tqdm import tqdm

@click.command()
@click.option(
    "--input-file",
    help="The input geotiff",
    default="data/temp/snow_conus.tif",
)
@click.option(
    "--output-file",
    help="The output geotiff",
    default="data/temp/quantized.tif",
)
@click.option(
    "--bin-size",
    help="The size of bins with which to quantize the input file, in inches",
    default=12,
)
@click.option(
    "--bbox",
    help="The bounding box to trim the output",
    default=None,
)
def cli(input_file, output_file, bin_size, bbox):
    with rasterio.open(input_file) as src:
     
        if bbox:
            # clip the data to bounding box 
            x_min, y_min, x_max, y_max = bbox.split(",")
            x_min, y_min, x_max, y_max = float(x_min), float(y_min), float(x_max), float(y_max)
            window = rasterio.windows.from_bounds(x_min, y_min, x_max, y_max, src.transform)
            data = src.read(1, window=window)
        else:
            data = src.read(1)

        # set nodata values to 0
        data[data == src.meta['nodata']] = 0
        # values are in milimeters, convert to inches
        data = data * 0.0393701
        
        # divide the range into bins
        thresholds = np.arange(0, np.max(data), bin_size)
        print("Contour thresholds, in inches")
        print(thresholds)
        
        # Apply quantization thresholds
        quantized_data = np.digitize(data, thresholds, right=True)
        out_data = np.zeros_like(data)

        rows, columns = quantized_data.shape
        # convert each value in the raster to its bin's value
        for j in tqdm(range(columns)):
            for i in range(rows):
                bin_index = quantized_data[i,j]

                if data[i,j] == src.meta['nodata']:
                    bin_value = src.meta['nodata']
                if bin_index == len(thresholds):
                    # value greater than last threshold gets set to last threshold
                    bin_value =  thresholds[-1]
                else: 
                    bin_value = thresholds[bin_index]
                    # 0 values get set to no data
                    if bin_value == 0:
                        bin_value = src.meta['nodata']

                out_data[i,j] = bin_value

        meta = src.meta.copy()
        # set the meta based on new bounding box 
        if bbox:
            meta['height'] = out_data.shape[0]
            meta['width'] = out_data.shape[1]
            meta['transform'] = rasterio.windows.transform(window, src.transform)
        
        with rasterio.open(output_file, 'w', **meta) as dst:
            dst.write(out_data, 1)

if __name__ == "__main__":
    cli()

