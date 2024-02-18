import fiona
import glob
import click
import os

from fiona.crs import from_epsg
from shapely.geometry import box, shape, MultiPolygon, mapping
from tqdm import tqdm

from utils import clean_attributes


@click.command()
@click.option(
    "--bbox",
    default="-124.566244,46.864746,-116.463504,41.991794",
    help="Bounding box to trim the sources",
)
@click.option(
    "--usfs-input-file",
    help="The USFS wildfire perimeter shapefile",
    default="data/sources/USFSPerimeters/*.shp",
)
@click.option(
    "--blm-input-file",
    help="The BLM wildfire perimeter shapefile",
    default="data/sources/BLMPerimeters/*.shp",
)
@click.option(
    "--nifc-input-file",
    help="The NIFC wildfire perimeter shapefile",
    default="data/sources/NIFCPerimeters/*.shp",
)
@click.option(
    "--output-file",
    help="The output geopackage",
    default="data/temp/wildfires.gpkg",
)
def cli(bbox, usfs_input_file, blm_input_file, nifc_input_file, output_file):
    # make the path to the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    xmin, ymin, xmax, ymax = [float(x) for x in bbox.split(",")]
    bounding_box = box(xmin, ymin, xmax, ymax)

    usfs_file = None
    blm_file = None
    nifc_file = None

    # Load fire datasets
    print("Loading fire datasets...")
    if len(glob.glob(usfs_input_file)) == 0:
        print("No USFS shapefile found at path {}".format(usfs_input_file))
    else:
        usfs_file = glob.glob(usfs_input_file)[0]

    if len(glob.glob(blm_input_file)) == 0:
        print("No BLM shapefile found at path {}".format(blm_input_file))
    else:
        blm_file = glob.glob(blm_input_file)[0]

    if len(glob.glob(nifc_input_file)) == 0:
        print("No NIFC shapefile found at path {}".format(nifc_input_file))
    else:
        nifc_file = glob.glob(nifc_input_file)[0]

    if usfs_file == None and blm_file == None and nifc_file == None:
        raise Exception("No shapefiles provided")

    def process_usfs_feature(feature):
        # check if the bounding box intersects the geometry
        try:
            geometry = shape(feature["geometry"])
            clipped_geometry = geometry.intersection(bounding_box)
        except Exception:
            # if the geometry is invalid, skip it
            return

        if clipped_geometry.is_empty:
            return

        if feature["properties"].get("FIREYEAR", None) == None:
            return

        attributes = {
            "name": feature["properties"].get("FIRENAME", None),
            "year": feature["properties"].get("FIREYEAR", None),
            "agency": feature["properties"].get("OWNERAGENC", None),
            "cause1": None,
            "cause2": feature["properties"].get("STATCAUSE", None),
            "cause3": None,
            "startdate": feature["properties"].get("DISCOVERYD", None),
            "enddate": None,
            "source": "USFS",
        }
        attributes = clean_attributes.standardize_year(attributes)
        attributes = clean_attributes.standardize_name(attributes)
        attributes = clean_attributes.standardize_causes(attributes)

        return {"properties": attributes, "geometry": shape(feature["geometry"])}

    cleaned_usfs_features = []

    if usfs_file != None:
        with fiona.open(usfs_file, "r") as shapefile:
            for feature in tqdm(shapefile):
                res = process_usfs_feature(feature)
                if res != None:
                    cleaned_usfs_features.append(res)

    def process_blm_feature(feature):
        try:
            geometry = shape(feature["geometry"])
            clipped_geometry = geometry.intersection(bounding_box)
        except Exception:
            return

        if clipped_geometry.is_empty:
            return

        if feature["properties"].get("FIRE_DSCVR", None) == None:
            return

        attributes = {
            "name": feature["properties"].get("INCDNT_NM", None),
            "year": feature["properties"].get("FIRE_DSCVR", None),
            "agency": None,
            "cause1": feature["properties"].get("FIRE_CAUSE", None),
            "cause2": None,
            "cause3": None,
            "startdate": feature["properties"].get("FIRE_DSC_1", None),
            "enddate": feature["properties"].get("FIRE_CNTRL", None),
            "source": "BLM",
        }
        attributes = clean_attributes.standardize_year(attributes)
        attributes = clean_attributes.standardize_name(attributes)
        attributes = clean_attributes.standardize_causes(attributes)

        return {"properties": attributes, "geometry": shape(feature["geometry"])}

    cleaned_blm_features = []

    if blm_file != None:
        with fiona.open(blm_file, "r") as shapefile:
            for feature in tqdm(shapefile):
                res = process_blm_feature(feature)
                if res != None:
                    cleaned_blm_features.append(res)

    def process_nifc_feature(feature):
        try:
            geometry = shape(feature["geometry"])
            clipped_geometry = geometry.intersection(bounding_box)
        except Exception:
            return

        if clipped_geometry.is_empty:
            return

        attributes = {
            "name": feature["properties"].get("poly_Incid", None),
            "year": None,
            "agency": feature["properties"].get("attr_POOLa", None),
            "cause1": feature["properties"].get("attr_FireC", None),
            "cause2": feature["properties"].get("attr_Fir_4", None),
            "cause3": feature["properties"].get("attr_Fir_5", None),
            "startdate": feature["properties"].get("attr_Fir_7", None),
            "enddate": feature["properties"].get("attr_Conta", None),
            "source": "NIFC",
        }

        if feature["properties"].get("STARTDATE", None) == None:
            attributes["year"] = attributes["startdate"][:4]

        if attributes.get("year", None) == None or attributes.get("year", None) == "":
            return

        attributes = clean_attributes.standardize_year(attributes)
        attributes = clean_attributes.standardize_name(attributes)
        attributes = clean_attributes.standardize_causes(attributes)

        return {"properties": attributes, "geometry": shape(feature["geometry"])}

    cleaned_nifc_features = []

    if nifc_file != None:
        with fiona.open(nifc_file, "r") as shapefile:
            for feature in tqdm(shapefile):
                res = process_nifc_feature(feature)
                if res != None:
                    cleaned_nifc_features.append(res)

    print(
        f"Found {len(cleaned_usfs_features)} USFS features, {len(cleaned_blm_features)} BLM features, and {len(cleaned_nifc_features)} NIFC features"
    )

    # save the features to a geopackage
    print("Saving features to geopackage...")

    output_features = (
        cleaned_usfs_features + cleaned_blm_features + cleaned_nifc_features
    )
    schema = {
        "geometry": "MultiPolygon",
        "properties": {
            "name": "str",
            "year": "int",
            "agency": "str",
            "cause1": "str",
            "cause2": "str",
            "cause3": "str",
            "startdate": "str",
            "enddate": "str",
            "source": "str",
        },
    }

    with fiona.open(
        output_file, "w", driver="GPKG", schema=schema, crs=from_epsg(4326)
    ) as output_geopackage:
        for feature in tqdm(output_features):
            geom = shape(feature["geometry"])
            if geom.geom_type == "Polygon":
                geom = MultiPolygon([geom])

            feature["geometry"] = mapping(geom)

            output_geopackage.write(feature)


if __name__ == "__main__":
    cli()
