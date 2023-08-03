import jellyfish
import geopy.distance

from alive_progress import alive_bar

import geopandas as gpd
import numpy as np

from shapely.geometry.polygon import orient


# https://gis.stackexchange.com/questions/413349/calculating-area-of-lat-lon-polygons-without-transformation-using-geopandas
def get_geographic_area(geodf):
    if not (geodf.crs and geodf.crs.is_geographic):
        raise TypeError(
            'geodataframe should have geographic coordinate system')

    with alive_bar(len(geodf.index), title="Calculating geometry areas...", force_tty=True) as bar:
        geod = geodf.crs.get_geod()

        def area_calc(geom, skip_bar=False):
            if geom.geom_type not in ['MultiPolygon', 'Polygon']:
                return np.nan

            # For MultiPolygon do each separately
            if geom.geom_type == 'MultiPolygon':
                r = np.sum([area_calc(p, True) for p in geom.geoms])
                bar()
                return r
            else:
                # orient to ensure a counter-clockwise traversal.
                # See https://pyproj4.github.io/pyproj/stable/api/geod.html
                # geometry_area_perimeter returns (area, perimeter)
                r = geod.geometry_area_perimeter(orient(geom, 1))[0]
                if not skip_bar:
                    bar()
                return r

        return geodf.geometry.apply(area_calc)


# get the percent difference between two areas
def get_area_diff(area_r1_m2, area_r2_m2):
    return abs(area_r1_m2 - area_r2_m2) / ((area_r1_m2 + area_r2_m2) / 2)


# the difference in area must be no more than 20% and distnace no more than 1500m
AREA_THRESHOLD = 0.2
DISTANCE_THRESHOLD = 1500


# check if two regions are the same based on their geometry
def same_geom_heuristic(r1, r2):
    n1 = r1['NAME']
    n2 = r2['NAME']
    if n2 == n2 or jellyfish.jaro_winkler_similarity(n1, n2) < 0.5:
        # check that the two have a similar size
        percent_diff = get_area_diff(r1['AREA'], r2['AREA'])
        if percent_diff < AREA_THRESHOLD:
            # now check that their centroids are an allowable distance apart
            c1 = r1['CENTROID']
            c2 = r2['CENTROID']
            dist = geopy.distance.geodesic((c1.y, c1.x), (c2.y, c2.x))

            if dist.meters <= DISTANCE_THRESHOLD:

                g1 = gpd.GeoSeries(r1['geometry'])
                g2 = gpd.GeoSeries(r2['geometry'])
                intersects = g1.intersects(g2).any()

                return intersects

    return False
