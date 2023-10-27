import click
import os

from tqdm import tqdm
from osgeo import ogr, gdal

gdal.UseExceptions()


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

    # Create a temp shapefile for the clipped features
    driver = ogr.GetDriverByName("GeoJSON")
    temp_ds = driver.CreateDataSource(os.path.join(output_dir, "temp.geojson"))
    temp_layer = temp_ds.CreateLayer(
        "glaciers", geom_type=ogr.wkbPolygon, srs=layer.GetSpatialRef()
    )

    glac_name_field = ogr.FieldDefn("glac_name", ogr.OFTString)
    glac_name_field.SetWidth(254)
    temp_layer.CreateField(glac_name_field)

    glac_area_field = ogr.FieldDefn("area", ogr.OFTReal)
    glac_area_field.SetWidth(254)
    temp_layer.CreateField(glac_area_field)

    anlys_time_field = ogr.FieldDefn("anlys_time", ogr.OFTString)
    anlys_time_field.SetWidth(254)
    temp_layer.CreateField(anlys_time_field)

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

            if clipped_geometry is None:
                continue
            if clipped_geometry.GetGeometryName() != "POLYGON":
                continue

            if not clipped_geometry.IsValid():
                clipped_geometry = clipped_geometry.MakeValid()
                if clipped_geometry is None:
                    continue

            # verify the anlys_time is greater than or equal to the filter year
            # format will be like 2023-02-16T00:00:00
            anlys_time = feature.GetField("anlys_time")
            if anlys_time is None:
                continue

            anlys_year = int(anlys_time.split("-")[0])
            if anlys_year < int(filter_year):
                continue

            clipped_feature = ogr.Feature(temp_layer.GetLayerDefn())

            glac_name = feature.GetField("glac_name")

            # only add the glacier name if it contains the word "Glacier"
            # this will not work for glaciers outside the US
            if "Glacier" in glac_name:
                clipped_feature.SetField("glac_name", glac_name)

            clipped_feature.SetField("anlys_time", anlys_time)
            clipped_feature.SetField("area", feature.GetField("area"))

            clipped_feature.SetGeometry(clipped_geometry)
            temp_layer.CreateFeature(clipped_feature)

    ds = None
    temp_ds = None

    print("Combining features...")

    ds = ogr.Open(os.path.join(output_dir, "temp.geojson"), 0)
    layer = ds.GetLayer()

    out_ds = driver.CreateDataSource(output_file)
    out_layer = out_ds.CreateLayer(
        "glaciers", geom_type=ogr.wkbPolygon, srs=layer.GetSpatialRef()
    )

    glac_name_field = ogr.FieldDefn("glac_name", ogr.OFTString)
    glac_name_field.SetWidth(254)
    out_layer.CreateField(glac_name_field)

    glac_area_field = ogr.FieldDefn("area", ogr.OFTReal)
    glac_area_field.SetWidth(254)
    out_layer.CreateField(glac_area_field)

    anlys_time_field = ogr.FieldDefn("anlys_time", ogr.OFTString)
    anlys_time_field.SetWidth(254)
    out_layer.CreateField(anlys_time_field)

    named_feats = [
        feature for feature in layer if feature.GetField("glac_name") is not None
    ]
    unnamed_feats = [
        feature for feature in layer if feature.GetField("glac_name") is None
    ]

    # copy over the named glaciers first
    for feature in tqdm(named_feats):
        geom = feature.GetGeometryRef()
        new_feat = ogr.Feature(layer.GetLayerDefn())
        new_feat.SetField("glac_name", feature.GetField("glac_name"))
        new_feat.SetField("anlys_time", feature.GetField("anlys_time"))
        new_feat.SetField("area", feature.GetField("area"))
        new_feat.SetGeometry(geom)
        out_layer.CreateFeature(new_feat)
        continue

    out_layer.SyncToDisk()

    named_feats = [feature for feature in out_layer]

    print(len(named_feats))

    # search through the named glaciers and find any that share an edge
    # combine them into a single feature if they do
    for feature in tqdm(unnamed_feats):
        geom = feature.GetGeometryRef()

        intersecting_geoms = []
        buffered_geom = geom.Buffer(0.0001)
        # search for overlapping named glaciers
        for feature2 in named_feats:
            print("test")
            geom2 = feature2.GetGeometryRef()
            buffered_geom2 = geom2.Buffer(0.0001)
            if buffered_geom.Intersects(buffered_geom2):
                intersecting_geoms.append(geom2)

        if len(intersecting_geoms) == 0:
            # no intersecting geometries; just add this feature
            new_feat = ogr.Feature(layer.GetLayerDefn())
            new_feat.SetField("anlys_time", feature.GetField("anlys_time"))
            new_feat.SetField("area", feature.GetField("area"))
            new_feat.SetGeometry(geom)
            out_layer.CreateFeature(new_feat)
            continue
        else:
            # there are intersecting geometries; combine the unnamed feature with the existing feature
            # and update the existing feature's geometry with the union
            new_geom = geom
            for geom2 in intersecting_geoms:
                new_geom = new_geom.Union(geom2)

            out_layer.DeleteFeature(feature2.GetFID())
            feature2.SetGeometry(new_geom)
            out_layer.SetFeature(feature2)
            # update the named feats list
            named_feats = [feature for feature in out_layer]
            continue


if __name__ == "__main__":
    cli()
