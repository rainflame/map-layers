def standardize_year(attributes):
    # convert fire year to datetime 
    if attributes["year"] != None:
        attributes["year"] = str(int(attributes["year"]))

    return attributes

def standardize_name(attributes):
    # clean up name values
    if attributes["name"] == None:
        attributes["name"] = "unnamed fire"

    attributes["name"] =  attributes["name"].lower()
    attributes["name"] =  attributes["name"].replace('unnamed', 'unnamed fire')
    attributes["name"] =  attributes["name"].replace('noname', 'unnamed fire')
    attributes["name"] =  attributes["name"].replace('unknown', 'unnamed fire')
    attributes["name"] =  attributes["name"].replace('missing', 'unnamed fire')
    attributes["name"] =  attributes["name"].replace('n/a', 'unnamed fire')

    return attributes



def standardize_causes(attributes):

    if attributes["cause2"] != None:
        attributes["cause2"] = attributes["cause2"].lower()

    if attributes["cause1"] != None:
        attributes["cause1"] = attributes["cause1"].lower()

    if attributes["cause3"] != None:
        attributes["cause3"] = attributes["cause3"].lower()

    
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
        if attributes["cause2"] != None and num in attributes['cause2']:
            attributes['cause2'] = cause

    # remap layer 2 causes to a standardized set of cases
    layer_2_cause_map = {
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
        if attributes["cause2"] != None and og_cause in attributes['cause2']:
            attributes['cause2'] = cause

    # generate layer 1 causes from layer 2 causes
    layer_1_cause_map = {
        'human': 'human',
        'natural': 'natural',
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

    if attributes['cause1'] == None and attributes['cause2'] != None:
        attributes['cause1'] = layer_1_cause_map[attributes['cause2']]

    return attributes