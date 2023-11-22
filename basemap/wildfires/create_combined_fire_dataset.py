import glob
import json
import numpy as np

from datetime import datetime, timezone
from shapely.geometry import Point

import geopandas as gpd
import pandas as pd


from alive_progress import alive_bar

from utils.geometry import get_geographic_area, same_geom_heuristic
from utils.shapefile import load_shapefile


# Load fire datasets
print("Loading fire datasets...")


usfs_path = "data/sources/USFSPerimeters/*.shp"
if len(glob.glob(usfs_path)) == 0:
    raise Exception("No USFS shapefile found at path {}".format(usfs_path))
else:
    usfs_df = load_shapefile(
        glob.glob(usfs_path)[0])


blm_path = "data/sources/BLMPerimeters/*.shp"
if len(glob.glob(blm_path)) == 0:
    raise Exception("No BLM shapefile found at path {}".format(blm_path))
else:
    blm_df = load_shapefile(
        glob.glob(blm_path)[0])


nifc_path = "data/sources/NIFCPerimeters/*.shp"
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
        df.loc[df['CAUSE_2'] == num, 'CAUSE_2'] = cause

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
        df.loc[df['CAUSE_2'] == og_cause, 'CAUSE_2'] = cause

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
        if pd.isnull(row['CAUSE_1']):
            try:
                return layer_1_cause_map[row['CAUSE_2']]
            except KeyError as e:
                return None
        return row['CAUSE_1']

    df['CAUSE_1'] = df.apply(create_layer_1_value, axis=1)

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
    'STATCAUSE': 'CAUSE_2',
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
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('unnamed', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('noname', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('unknown', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('missing', 'unnamed fire')
usfs_df_st['NAME'] = usfs_df_st['NAME'].replace('n/a', 'unnamed fire')

# clean up cause values
usfs_df_st['CAUSE_2'] = usfs_df_st['CAUSE_2'].str.lower()
usfs_df_st['CAUSE_1'] = None
usfs_df_st['CAUSE_3'] = None

usfs_df_st = standardize_causes(usfs_df_st)


# Clean the BLM dataset.
print("Cleaning BLM dataset...")
########################################################################

# Select only the columns of interest.
# https://gbp-blm-egis.hub.arcgis.com/datasets/BLM-EGIS::blm-natl-fire-perimeters-polygon/about
blm_remap = {
    'INCDNT_NM': 'NAME',
    'FIRE_DSCVR': 'YEAR',
    'FIRE_CAUSE': 'CAUSE_1',
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
blm_df_st['NAME'] = blm_df_st['NAME'].replace('not available', 'unnamed fire')
blm_df_st['NAME'] = blm_df_st['NAME'].replace('unnamed', 'unnamed fire')
blm_df_st['NAME'] = blm_df_st['NAME'].replace('unknown', 'unnamed fire')

# standardize causes
blm_df_st['CAUSE_1'] = blm_df_st['CAUSE_1'].str.lower()
blm_df_st['CAUSE_1'] = blm_df_st['CAUSE_1'].replace('uk', None)
blm_df_st['CAUSE_1'] = blm_df_st['CAUSE_1'].replace(
    'unknown', None)
blm_df_st['CAUSE_1'].fillna('undetermined', inplace=True)
blm_df_st['CAUSE_2'] = None
blm_df_st['CAUSE_3'] = None

blm_df_st['ENDDATE'] = blm_df_st['ENDDATE'].replace('9999-09-09', None)


# Clean the NIFC dataset.
print("Cleaning NIFC dataset...")
########################################################################

# Select only the columns of interest.

# https://data-nifc.opendata.arcgis.com/datasets/nifc::wfigs-interagency-fire-perimeters/about
nifc_remap = {
    'poly_Incid': 'NAME',
    # XXX: 'YEAR', # will need to calculate this from STARTDATE
    'attr_FireC': 'CAUSE_1',
    'attr_Fir_4': 'CAUSE_2',
    'attr_Fir_5': 'CAUSE_3',
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
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('unnamed', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('noname', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('unknown', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('missing', 'unnamed fire')
nifc_df_st['NAME'] = nifc_df_st['NAME'].replace('n/a', 'unnamed fire')

# clean up cause values
nifc_df_st['CAUSE_1'] = nifc_df_st['CAUSE_1'].str.lower()
nifc_df_st['CAUSE_2'] = nifc_df_st['CAUSE_2'].str.lower()
nifc_df_st['CAUSE_3'] = nifc_df_st['CAUSE_3'].str.lower()

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
all_fires_df.set_crs("EPSG:4326", inplace=True)
all_fires_df['AREA'] = get_geographic_area(all_fires_df)


def find_fire_groups(groups, n):
    with alive_bar(groups.ngroups, title="Grouping similar fires, pass {}...".format(n), force_tty=True) as bar:
        fire_groups_list = []
        for _, group in groups:
            n = len(group.index)
            colors = np.arange(n)

            # color rows by first row that is transitively close to it
            for i in range(n):
                for j in range(i+1, n):
                    if same_geom_heuristic(group.iloc[i], group.iloc[j]):
                        colors[j] = colors[i]

            group['COLOR'] = colors
            cgroups = group.groupby(['COLOR'])
            fire_groups_list += [cgroup for _, cgroup in cgroups]

            bar()

    fire_df = pd.concat(fire_groups_list)
    return fire_df


class GroupError(Exception):
    pass


def flatten_group_to_row(group):
    # Prefer rows given this particular ordering of sources.
    source_rows = {}
    for _, row in group.iterrows():
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
        if row['CAUSE_3']:
            cause_specificity[3].append(row)
        elif row['CAUSE_2']:
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

    # Somewhat arbitrarily choose the last entry.
    # This is deterministic assuming rows maintain order throughout all previous operations.
    final_row = ref_rows[-1]
    return final_row


def combine_groups(groups):
    combined_list = []
    with alive_bar(groups.ngroups, title="Combining duplicate rows...", force_tty=True) as bar:
        for _, group in groups:
            try:
                row = flatten_group_to_row(group)
            except GroupError as e:
                print("ERROR: {}".format(e))
                continue
            combined_list.append(row)
            bar()

    df = gpd.GeoDataFrame(combined_list)
    return df


# Find groups of fires with the same name and year that are likely duplicates.
groups = all_fires_df.groupby(['NAME', 'YEAR'])
temp_df1 = find_fire_groups(groups, 1)
fire_groups1 = temp_df1.groupby(['NAME', 'YEAR', 'COLOR'])
fire_dedupped1 = combine_groups(fire_groups1)

print("Dedupped from {} to {} rows".format(
    len(all_fires_df.index), len(fire_dedupped1.index)))


# now find groups of fires with the same year that are likely duplicates
groups = fire_dedupped1.groupby(['YEAR'])
temp_df2 = find_fire_groups(groups, 2)
fire_groups2 = temp_df2.groupby(['YEAR', 'COLOR'])
fire_dedupped2 = combine_groups(fire_groups2)

print("Dedupped from {} to {} rows".format(
    len(fire_dedupped1.index), len(fire_dedupped2.index)))


print("Writing final dataset to shapefile...")
########################################################################

# Create a df ready to export as a shapefile.
out_df = fire_dedupped2.copy()

# convert AREA from square meters to acres
out_df['AREA'] = out_df['AREA'] * 0.0002471054

# convert YEAR to int
out_df['YEAR'] = out_df['YEAR'].astype(int)

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
