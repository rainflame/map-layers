import glob
import json
import numpy as np

from datetime import datetime, timezone
from shapely.geometry import shape, Point
from shapely.geometry.polygon import orient

import geopandas as gpd
import pandas as pd

import fiona

from alive_progress import alive_bar
import geopy.distance


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


# Load fire datasets

print("Loading fire datasets...")

usfs_path = "data/USFSPerimeters/*.shp"
if len(glob.glob(usfs_path)) == 0:
    raise Exception("No USFS shapefile found at path {}".format(usfs_path))
else:
    usfs_df = load_shapefile(
        glob.glob(usfs_path)[0])


blm_path = "data/BLMPerimeters/*.shp"
if len(glob.glob(blm_path)) == 0:
    raise Exception("No BLM shapefile found at path {}".format(blm_path))
else:
    blm_df = load_shapefile(
        glob.glob(blm_path)[0])


nifc_path = "data/NIFCPerimeters/*.shp"
if len(glob.glob(nifc_path)) == 0:
    raise Exception("No NIFC shapefile found at path {}".format(nifc_path))
else:
    nifc_df = load_shapefile(
        glob.glob(nifc_path)[0])


def standardize_causes(df):

    # remap usfs cause codes to their corresponding causes
    usfs_cause_map = {
        '1': 'lightning',
        '2': 'equipment',
        '3': 'smoking',
        '4': 'campfire',
        '5': 'debris burning',
        '6': 'railroad',
        '7': 'arson',
        '8': 'children',
        '9': 'miscellaneous',
    }

    for num, cause in usfs_cause_map.items():
        df.loc[df['CAUSE_DETAIL_2'] == num, 'CAUSE_DETAIL_2'] = cause

    # remap layer 2 causes to a standardized set of cases
    layer_2_cause_map = {
        None: None,
        'campfire': 'camping',
        'equipment': 'equipment and vehicle use',
        'children': 'misuse of fire by a minor',
        '5-debris burning': 'debris and open burning',
        'debris/open burning': 'debris and open burning',
        'debris burning': 'debris and open burning',
        'railroad': 'railroad operations and maintenance',
        'firearms and explosives use': 'firearms and weapons',
        'firearms/weapons': 'firearms and weapons',
        'power generation/transmission/distribution': 'utilities',
        'incindiary': 'incendiary',
        '7-arson': 'arson',
        'undetermined': None,
        'miscellaneous': None,
        'undetermined (remarks required)': None,
        'cause and origin not identified': None,
        'investigated but undetermined': None,
        'investigated but und': None,
        'cause not identified': None,
        'undetermined (remar*': None,
        '9 - miscellaneous': None,
        '10': None,
        '14': None,
        '0': None
    }

    for og_cause, cause in layer_2_cause_map.items():
        df.loc[df['CAUSE_DETAIL_2'] == og_cause, 'CAUSE_DETAIL_2'] = cause

    # existing layer 2 causes common in both datasets
    # 'incendiary'
    # 'lightning'
    # 'camping'
    # 'recreation and ceremony'
    # 'other human cause'
    # 'other natural cause'
    # 'arson'
    # 'coal seam'
    # 'smoking'
    # 'utilities'

    # generate layer 1 causes from layer 2 causes
    layer_1_cause_map = {
        'human': 'human',
        'natural': 'natural',
        None: None,
        'equipment and vehicle use': 'human',
        'misuse of fire by a minor': 'human',
        'debris and open burning': 'human',
        'railroad operations and maintenance': 'human',
        'firearms and weapons': 'human',
        'incendiary': 'human',
        'camping': 'human',
        'recreation and ceremony': 'human',
        'arson': 'human',
        'smoking': 'human',
        'utilities': 'human',
        'other human cause': 'human',
        'coal seam': 'human',
        'lightning': 'natural',
        'other natural cause': 'natural',
        'volcanic': 'natural',
        'undetermined': None
    }

    def create_layer_1_value(row):
        if pd.isnull(row['CAUSE_DETAIL_1']):
            try:
                return layer_1_cause_map[row['CAUSE_DETAIL_2']]
            except KeyError as e:
                return None
        return row['CAUSE_DETAIL_1']

    df['CAUSE_DETAIL_1'] = df.apply(create_layer_1_value, axis=1)

    return df


# Clean the USFS dataset.
print("Cleaning USFS dataset...")
########################################################################

# Select only the columns of interest.
# https://data.fs.usda.gov/geodata/edw/edw_resources/meta/S_USA.FinalFirePerimeter.xml
usfs_remap = {
    'FIRENAME': 'NAME',
    'FIREYEAR': 'YEAR',
    'OWNERAGENC': 'AGENCY',
    'STATCAUSE': 'CAUSE_DETAIL_2',
    'DISCOVERYD': 'STARTDATE',
    'geometry': 'geometry',
}
usfs_df_sel = usfs_df.rename(columns=usfs_remap)
usfs_df_sel = usfs_df_sel[list(usfs_remap.values())]


# Standardize the USFS dataset.
# no endtime in this dataset, but add the column anyway
usfs_df_st = usfs_df_sel.copy()
usfs_df_st['ENDDATE'] = None
usfs_df_st['SOURCE'] = 'USFS'


# drop rows where year is null
usfs_df_st = usfs_df_st.dropna(subset=['YEAR'])

# convert year to datetime
usfs_df_st['YEAR'] = usfs_df_st['YEAR'].astype(int).astype(str)

# clean up name values
usfs_df_st['NAME'] = usfs_df_st['NAME'].str.lower()
usfs_df_st['NAME'].fillna('unnamed fire', inplace=True)
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('noname', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('unknown', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('missing', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('n/a', 'unnamed fire')

# clean up cause values
usfs_df_st['CAUSE_DETAIL_2'] = usfs_df_st['CAUSE_DETAIL_2'].str.lower()
usfs_df_st['CAUSE_DETAIL_1'] = None
usfs_df_st['CAUSE_DETAIL_3'] = None

usfs_df_st = standardize_causes(usfs_df_st)


# Clean the BLM dataset.
print("Cleaning BLM dataset...")
########################################################################

# Select only the columns of interest.
# https://gbp-blm-egis.hub.arcgis.com/datasets/BLM-EGIS::blm-natl-fire-perimeters-polygon/about
blm_remap = {
    'INCDNT_NM': 'NAME',
    'FIRE_DSCVR': 'YEAR',
    'FIRE_CAUSE': 'CAUSE_DETAIL_1',
    'FIRE_DSC_1': 'STARTDATE',
    'FIRE_CNTRL': 'ENDDATE',
    'geometry': 'geometry',
}
blm_df_sel = blm_df.rename(columns=blm_remap)
blm_df_sel = blm_df_sel[list(blm_remap.values())]


# Standardize the BLM dataset.
blm_df_st = blm_df_sel.copy()
blm_df_st['SOURCE'] = 'BLM'

# drop rows where year is null
blm_df_st = blm_df_st.dropna(subset=['YEAR'])

# convert year to datetime
blm_df_st['YEAR'] = blm_df_st['YEAR'].astype(int).astype(str)

# clean up name values
blm_df_st['NAME'] = blm_df_st['NAME'].str.lower()
blm_df_st['NAME'].fillna('unnamed fire', inplace=True)

# standardize causes
blm_df_st['CAUSE_DETAIL_1'] = blm_df_st['CAUSE_DETAIL_1'].str.lower()
blm_df_st['CAUSE_DETAIL_1'] = blm_df_st['CAUSE_DETAIL_1'].replace('uk', None)
blm_df_st['CAUSE_DETAIL_1'] = blm_df_st['CAUSE_DETAIL_1'].replace(
    'unknown', None)
blm_df_st['CAUSE_DETAIL_1'].fillna('undetermined', inplace=True)
blm_df_st['CAUSE_DETAIL_2'] = None
blm_df_st['CAUSE_DETAIL_3'] = None

blm_df_st['ENDDATE'] = blm_df_st['ENDDATE'].replace('9999-09-09', None)


# Clean the NIFC dataset.
print("Cleaning NIFC dataset...")
########################################################################

# Select only the columns of interest.

# https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters/about
nifc_remap = {
    'poly_Incid': 'NAME',
    # XXX: 'YEAR', # will need to calculate this from STARTDATE
    'attr_FireC': 'CAUSE_DETAIL_1',
    'attr_Fir_4': 'CAUSE_DETAIL_2',
    'attr_Fir_5': 'CAUSE_DETAIL_3',
    'attr_POOLa': 'AGENCY',
    'attr_Fir_7': 'STARTDATE',
    'attr_Conta': 'ENDDATE',
    'geometry': 'geometry',
}
nifc_df_sel = nifc_df.rename(columns=nifc_remap)
nifc_df_sel = nifc_df_sel[list(nifc_remap.values())]

# Standardize the NIFC dataset.
nifc_df_st = nifc_df_sel.copy()

# compute year from STARTDATE
nifc_df_st['YEAR'] = [e[:4] for e in nifc_df_st['STARTDATE']]

nifc_df_st['SOURCE'] = 'NIFC'

# clean up name values
nifc_df_st['NAME'] = nifc_df_st['NAME'].str.lower()
nifc_df_st['NAME'].fillna('unnamed fire', inplace=True)
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('noname', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('unknown', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('missing', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('n/a', 'unnamed fire')

# clean up cause values
nifc_df_st['CAUSE_DETAIL_1'] = nifc_df_st['CAUSE_DETAIL_1'].str.lower()
nifc_df_st['CAUSE_DETAIL_2'] = nifc_df_st['CAUSE_DETAIL_2'].str.lower()
nifc_df_st['CAUSE_DETAIL_3'] = nifc_df_st['CAUSE_DETAIL_3'].str.lower()

nifc_df_st = standardize_causes(nifc_df_st)


# Combine the datasets.
print("Combining datasets...")
########################################################################

all_fires_df = pd.concat([usfs_df_st, blm_df_st, nifc_df_st])

# remove old fires
all_fires_df = all_fires_df[all_fires_df['STARTDATE'] >= '1900-01-01']

# Calculate the centroids of each fire polygon.
print("Calculating fire geometry centroids...")
all_fires_df['CENTROID'] = all_fires_df.geometry.centroid.apply(Point)


# Calculate the area of each fire polygon (m^2).
# https://gis.stackexchange.com/questions/413349/calculating-area-of-lat-lon-polygons-without-transformation-using-geopandas

def gpd_geographic_area(geodf):
    if not (geodf.crs and geodf.crs.is_geographic):
        raise TypeError(
            'geodataframe should have geographic coordinate system')

    geod = geodf.crs.get_geod()

    def area_calc(geom):
        if geom.geom_type not in ['MultiPolygon', 'Polygon']:
            return np.nan

        # For MultiPolygon do each separately
        if geom.geom_type == 'MultiPolygon':
            return np.sum([area_calc(p) for p in geom.geoms])

        # orient to ensure a counter-clockwise traversal.
        # See https://pyproj4.github.io/pyproj/stable/api/geod.html
        # geometry_area_perimeter returns (area, perimeter)
        return geod.geometry_area_perimeter(orient(geom, 1))[0]

    return geodf.geometry.apply(area_calc)


all_fires_df.set_crs("EPSG:4326", inplace=True)
print("Recalculating fire areas...")
all_fires_df['AREA'] = gpd_geographic_area(all_fires_df)


# # Create a df ready to export as a shapefile.
# out_df = all_fires_df.copy()

# # export to shapefile does not handle GeometryDtype
# out_df = out_df.drop(columns=['CENTROID'])

# # set projection so can properly save geometry
# out_df.set_crs("EPSG:4326", inplace=True)

# # Convert dataframe to shapefile to analyze in QGIS.
# out_df.to_file("data/all_fire_groups.shp", driver='ESRI Shapefile')


T = 500  # threshold = 500 meters


def same_heuristic(r1, r2):
    c1 = r1['CENTROID']
    c2 = r2['CENTROID']
    dist = geopy.distance.geodesic((c1.y, c1.x), (c2.y, c2.x))
    return dist.meters < T


def find_fire_groups(df):
    groups = df.groupby(['NAME', 'YEAR'])

    with alive_bar(groups.ngroups, title="Finding distinct fires...", force_tty=True) as bar:
        fire_groups_list = []
        for name, group in groups:
            n = len(group.index)
            colors = np.arange(n)

            # color rows by first row that is transitively close to it
            for i in range(n):
                for j in range(i+1, n):
                    if same_heuristic(group.iloc[i], group.iloc[j]):
                        colors[j] = colors[i]

            group['COLOR'] = colors
            cgroups = group.groupby(['COLOR'])
            fire_groups_list += [cgroup for _, cgroup in cgroups]

            bar()

    fire_df = pd.concat(fire_groups_list)
    fire_groups = fire_df.groupby(['NAME', 'YEAR', 'COLOR'])
    return fire_groups


fire_groups = find_fire_groups(all_fires_df)
# fire_groups.ngroups


class GroupError(Exception):
    pass


def analysis(group):
    # Prefer rows given this particular ordering of sources.
    source_rows = {}
    for index, row in group.iterrows():
        source = row['SOURCE']
        if source not in source_rows:
            source_rows[source] = []
        source_rows[source].append(row)
    ref_rows_by_source = []
    for source in ['NIFC', 'USFS', 'BLM']:
        if source in source_rows:
            ref_rows_by_source = source_rows[source]
            break
    if len(ref_rows_by_source) == 0:
        raise GroupError("No rows for group by source")

    # Prefer rows with a more specific cause.
    cause_specificity = {1: [], 2: [], 3: []}
    for row in ref_rows_by_source:
        if row['CAUSE_DETAIL_3']:
            cause_specificity[3].append(row)
        elif row['CAUSE_DETAIL_2']:
            cause_specificity[2].append(row)
        else:
            cause_specificity[1].append(row)
    ref_rows_by_pref = []
    for preference in [3, 2, 1]:
        if len(cause_specificity[preference]) > 0:
            ref_rows_by_pref = cause_specificity[preference]
            break
    if len(ref_rows_by_pref) == 0:
        raise GroupError("No rows for group by cause specificity")

    ref_rows = ref_rows_by_pref

    # Identify and report conflicts in ref_rows.
    conflicts = []

    agencies = set([e['AGENCY'] for e in ref_rows])
    if len(agencies) > 1:
        conflicts.append("More than 1 agency: {}".format(agencies))

    cause1 = set([e['CAUSE_DETAIL_1'] for e in ref_rows])
    cause1_f = [e for e in cause1 if e != "undetermined"]
    if len(cause1_f) > 1:
        conflicts.append("More than one 1st-order cause: {}".format(cause1_f))

    cause2 = set([e['CAUSE_DETAIL_2'] for e in ref_rows])
    if len(cause2) > 1:
        conflicts.append("More than one 2nd-order cause: {}".format(cause2))

    cause3 = set([e['CAUSE_DETAIL_3'] for e in ref_rows])
    if len(cause3) > 1:
        conflicts.append("More than one 3rd-order cause: {}".format(cause3))

    start = set([e['STARTDATE'] for e in ref_rows if e['STARTDATE']])
    start_f = [e for e in start]
    if len(start_f) > 1:
        conflicts.append("More than one startdate: {}".format(start_f))

    end = set([e['ENDDATE'] for e in ref_rows if e['ENDDATE']])
    end_f = set([e for e in end])
    if len(end_f) > 1:
        conflicts.append("More than one enddate: {}".format(end_f))

    geos = [e['geometry'] for e in ref_rows]
    multiple = False
    for i in range(len(geos)):
        geo1 = geos[i]
        for j in range(i+1, len(geos)):
            geo2 = geos[j]
            if not geo1.equals_exact(geo2, 1e-6):
                multiple = True
                break
            if multiple:
                break
    if multiple:
        conflicts.append("More than one geometry")

    # if len(ref_rows) > 1:
    #    if len(conflicts) > 0:
    #        for conflict in conflicts:
    #            print(conflict)
    #        print()

    # Somewhat arbitrarily choose the last entry.
    # This is deterministic assuming rows maintain order throughout all previous operations.
    final_row = ref_rows[-1]
    return final_row


fires_list = []

with alive_bar(fire_groups.ngroups, title="Combining duplicate rows...", force_tty=True) as bar:
    for _, group in fire_groups:
        try:
            row = analysis(group)
        except GroupError as e:
            print("ERROR: {}".format(e))
            continue
        fires_list.append(row)
        bar()


fires_df = gpd.GeoDataFrame(fires_list)
print("Dedupped from {} to {} rows".format(
    len(all_fires_df.index), len(fires_df.index)))


print("Writing final dataset to shapefile...")

fires_df.rename(columns={'CAUSE_DETAIL_1': 'CAUSE_1',
                'CAUSE_DETAIL_2': 'CAUSE_2', 'CAUSE_DETAIL_3': 'CAUSE_3'}, inplace=True)

# convert AREA from square meters to acres
fires_df['AREA'] = fires_df['AREA'] * 0.0002471054

# Create a df ready to export as a shapefile.
out_df = fires_df.copy()

# export to shapefile does not handle GeometryDtype
out_df = out_df.drop(columns=['CENTROID'])

# set projection so can properly save geometry
out_df.set_crs("EPSG:4326", inplace=True)

# Convert dataframe to shapefile to analyze in QGIS.
out_df.to_file("data/fires.shp", driver='ESRI Shapefile')


now = datetime.now(timezone.utc)
now_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")

with open('data/meta.json', 'w') as f:
    json.dump({"updated": now_str}, f)

print("Done!")
