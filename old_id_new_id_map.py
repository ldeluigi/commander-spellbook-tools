import json
from urllib.request import Request, urlopen


def id_mapping() -> dict:
    sheet_combo_to_id = dict[frozenset[str], int]()
    # Commander Spellbook database fetching
    req = Request(
        'https://sheets.googleapis.com/v4/spreadsheets/1KqyDRZRCgy8YgMFnY0tHSw_3jC99Z0zFvJrPbfm66vA/values:batchGet?ranges=combos!A2:Q&key=AIzaSyBD_rcme5Ff37Evxa4eW5BFQZkmTbgpHew')
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        for row in data['valueRanges'][0]['values']:
            cards = frozenset(map(lambda name: name.lower().strip(' \t\n\r'), filter(
                lambda name: name is not None and len(name) > 0, row[1:11]))) - set([''])
            _id = int(row[0])
            sheet_combo_to_id[cards] = _id
    
    backend_combo_to_ids = dict[frozenset[str], tuple[int, str]]()
    req = Request(
        'https://backend.commanderspellbook.com/static/bulk/variants.json')
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        timestamp = data['timestamp']
        variants = data['variants']
        for variant in variants:
            combo_id = variant['id']
            unique_id = variant['unique_id']
            cards = frozenset(c['name'].lower().strip(' \t\n\r') for c in variant['includes'])
            backend_combo_to_ids[cards] = [combo_id, unique_id]
    
    result = dict()
    for combo, sheet_id in sheet_combo_to_id.items():
        if combo in backend_combo_to_ids:
            result[str(sheet_id)] = {
                'id': backend_combo_to_ids[combo][0],
                'unique_id': backend_combo_to_ids[combo][1]
            }
        else:
            result[str(sheet_id)] = {
                'id': None,
                'unique_id': None
            }
    
    return result


def id_mapping_to_json() -> str:
    return json.dumps(id_mapping(), indent=4)

print(id_mapping_to_json())