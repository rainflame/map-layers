import fiona
from alive_progress import alive_bar
from shapely.geometry import shape

import geopandas as gpd


def load_shapefile(file_path):
    with fiona.open(file_path, 'r') as shp:
        # read the features and handle broken geometries
        features = []
        with alive_bar(len(shp), title="Loading shapefile...", force_tty=True) as bar:
            for feature in shp:
                try:
                    # create a valid feature by fixing the geometry
                    valid_feature = {'geometry': shape(feature['geometry']).buffer(
                        0), 'properties': feature['properties']}
                    features.append(valid_feature)
                except Exception as e:
                    print("Error fixing geometry, skipping feature")
                bar()

    gdf = gpd.GeoDataFrame.from_features(features)
    gdf.crs = shp.crs
    # only keep polygons
    gdf = gdf[gdf.geometry.type != 'Point']

    return gdf
