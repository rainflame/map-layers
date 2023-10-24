import click
import os

from tqdm import tqdm
from osgeo import ogr


@click.command()
@click.option(
    "--bbox",
    default="-124.566244,46.864746,-116.463504,41.991794",
    help="Bounding box to trim the source shapefile.",
)
@click.option(
    "--filter-year",
    default="2023",
    help="The year to filter the glacier data. Any glaciers with a year greater than this will be removed.",
)
@click.option(
    "--input-file",
    default="data/sources/glims_polygons.shp",
    help="The input shapefile to trim and filter.",
)
@click.option(
    "--output-file",
    default="data/temp/glaciers.geojson",
    help="The output geojson file.",
)
def cli(bbox, filter_year, input_file, output_file):
    # make sure the path to the output exists, and if not make it
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # extract the bounding box coordinates
    xmin, ymin, xmax, ymax = [float(x) for x in bbox.split(",")]

    ds = ogr.Open(input_file)
    if ds is None:
        raise Exception(f"Failed to open {input_file}")
    layer = ds.GetLayer()

    # Create a new shapefile for the clipped features
    driver = ogr.GetDriverByName("GeoJSON")
    output_ds = driver.CreateDataSource(output_file)
    output_layer = output_ds.CreateLayer(
        "clipped_layer", geom_type=ogr.wkbPolygon, srs=layer.GetSpatialRef()
    )

    glac_name_field = ogr.FieldDefn("glac_name", ogr.OFTString)
    glac_name_field.SetWidth(254)
    output_layer.CreateField(glac_name_field)

    anlys_time_field = ogr.FieldDefn("anlys_time", ogr.OFTString)
    anlys_time_field.SetWidth(254)
    output_layer.CreateField(anlys_time_field)

    # create a geometry to represent the bounding box
    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xmin, ymin)
    ring.AddPoint(xmin, ymax)
    ring.AddPoint(xmax, ymax)
    ring.AddPoint(xmax, ymin)
    ring.AddPoint(xmin, ymin)
    bbox = ogr.Geometry(ogr.wkbPolygon)
    bbox.AddGeometry(ring)

    print("Clipping features...")
    for feature in tqdm(layer):
        geom = feature.GetGeometryRef()
        if geom.Intersects(bbox):
            clipped_geometry = geom.Intersection(bbox)

            # verify the geometry is a polygon
            if clipped_geometry.GetGeometryName() != "POLYGON":
                continue

            # verify the anlys_time is greater than or equal to the filter year
            # format will be like 2023-02-16T00:00:00
            anlys_time = feature.GetField("anlys_time")
            if anlys_time is None:
                continue
            anlys_year = int(anlys_time.split("-")[0])
            if anlys_year < int(filter_year):
                continue

            clipped_feature = ogr.Feature(output_layer.GetLayerDefn())
            glac_name = feature.GetField("glac_name")
            clipped_feature.SetField("glac_name", glac_name)
            clipped_feature.SetField("anlys_time", anlys_time)

            clipped_feature.SetGeometry(clipped_geometry)
            output_layer.CreateFeature(clipped_feature)

    # Clean up and close the datasets
    ds = None
    output_ds = None


if __name__ == "__main__":
    cli()
