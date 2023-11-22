import pandas as pd

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