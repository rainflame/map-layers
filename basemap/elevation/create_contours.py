import glob
import multiprocessing
import os
import click

from tqdm import tqdm
from osgeo import gdal, ogr, osr

# supress gdal exceptions
gdal.UseExceptions()


@click.command()
@click.option("--workers", default=4, help="Number of workers to use")
def cli(workers):
    # get all .tif files in the data/sources/ directory
    files = glob.glob("data/sources/*.tif")

    # create a data/temp/ directory if it doesn't exist
    try:
        os.mkdir("data/temp")
    except:
        pass

    # use multiprocessing to create the contours, reporting progress with tqdm
    with multiprocessing.Pool(processes=workers) as pool:
        for _ in tqdm(pool.imap_unordered(create_contours, files), total=len(files)):
            pass
        pool.close()
        pool.join()


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

    # create a new empty geojson dataset
    out_dataset = ogr.GetDriverByName("GeoJSONSeq").CreateDataSource(
        "data/temp/{}.geojson".format(file)
    )
    # see https://github.com/OSGeo/gdal/blob/83425621471d4987087317999d6fff3a482da88f/autotest/alg/contour.py#L105-L112
    contour_layer = out_dataset.CreateLayer("elevation", sr)
    field_defn = ogr.FieldDefn("ID", ogr.OFTInteger)
    contour_layer.CreateField(field_defn)
    field_defn = ogr.FieldDefn("elevation", ogr.OFTReal)
    contour_layer.CreateField(field_defn)

    try:
        gdal.ContourGenerate(vds.GetRasterBand(1), 40, 0, [], 0, 0, contour_layer, 0, 1)
    except:
        pass


if __name__ == "__main__":
    cli()
