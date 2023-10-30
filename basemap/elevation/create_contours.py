import glob
import multiprocessing
import os
import click
import shutil

from tqdm import tqdm
from osgeo import gdal, ogr, osr

# supress gdal exceptions
gdal.UseExceptions()


@click.command()
@click.option("--workers", default=multiprocessing.cpu_count(), help="Number of workers to use")
def cli(workers):
    # get all .tif files in the data/sources/ directory
    files = glob.glob("data/sources/*.tif")

    # create a data/temp/ directory if it doesn't exist
    try:
        if os.path.exists("data/temp"):
            shutil.rmtree("data/temp")
        os.mkdir("data/temp")
        for i in [40, 200, 1000]:
            os.mkdir("data/temp/{}".format(i))
    except:
        pass

    # use multiprocessing to create the contours, reporting progress with tqdm
    with multiprocessing.Pool(processes=workers) as pool:
        for _ in tqdm(pool.imap_unordered(create_contours, files), total=len(files)):
            pass
        pool.close()
        pool.join()


# scale the elevation values from meters to feet
translate_options = gdal.TranslateOptions(
    format="VRT",
    outputSRS="EPSG:4326",
    outputType=gdal.GDT_Float32,
    scaleParams=[[0.0, 0.3048, 0.0, 1.0]],
)


def create_contours(path):
    # get just the filename without the extension
    file = path.split("/")[-1].split(".")[0]
    ds = gdal.Open(path)
    # create a virtual dataset from the source file converting it to feet
    gdal.Translate("data/temp/{}.vrt".format(file), ds, options=translate_options)
    vds = gdal.Open("data/temp/{}.vrt".format(file))

    sr = osr.SpatialReference()
    sr.ImportFromEPSG(4326)

    # generate contours at 40, 200, and 1000 feet intervals
    for i in [40, 200, 1000]:

        # using geojsonseq to allow reading features in parallel with tippecanoe
        out_dataset = ogr.GetDriverByName("GeoJSONSeq").CreateDataSource(
            "data/temp/{}/{}.geojsons".format(i, file),
        )

        contour_layer = out_dataset.CreateLayer("elevation", sr)
        contour_layer.CreateField(ogr.FieldDefn("ID", ogr.OFTInteger))
        contour_layer.CreateField(ogr.FieldDefn("elevation", ogr.OFTReal))

        # create the contours
        try:
            gdal.ContourGenerate(vds.GetRasterBand(1), i, 0, [], 0, 0, contour_layer, 0, 1)
        except:
            print("error generating contours for {}".format(file))
            pass


if __name__ == "__main__":
    cli()
