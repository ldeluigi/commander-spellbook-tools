
from collections import defaultdict
import json
from urllib.request import Request, urlopen


def combos_including_other_combos() -> dict[int, tuple[frozenset[str], frozenset[int]]]:
    combo_db = list[frozenset[str]]()
    combo_to_id = dict[frozenset[str], int]()
    # Commander Spellbook database fetching
    req = Request(
        'https://sheets.googleapis.com/v4/spreadsheets/1KqyDRZRCgy8YgMFnY0tHSw_3jC99Z0zFvJrPbfm66vA/values:batchGet?ranges=combos!A2:Q&key=AIzaSyBD_rcme5Ff37Evxa4eW5BFQZkmTbgpHew')
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        for row in data['valueRanges'][0]['values']:
            cards = frozenset(map(lambda name: name.lower().strip(' \t\n\r'), filter(
                lambda name: name is not None and len(name) > 0, row[1:11]))) - set([''])
            id = int(row[0])
            combo_to_id[cards] = id
            if len(cards) <= 1:
                continue
            combo_db.append(cards)
    
    result = {combo_to_id[c]: (c, frozenset())  for c in combo_db}
    for combo in combo_db:
        for other in combo_db:
            if other.issubset(combo) and combo != other:
                result[combo_to_id[combo]] = (combo, result[combo_to_id[combo]][1] | frozenset([combo_to_id[other]]))
    return result

def pretty_print_combos_in_combos(combos: dict[int, tuple[frozenset[str], frozenset[int]]]) -> str:
    result = ''
    n = 1
    for id, (combo, includes) in sorted(combos.items(), key=lambda item: -len(item[1][0])):
        if len(includes) == 0:
            continue
        c = ', '.join(combo)
        result += f'{n}) The combo with id {id} ({c}) includes the following combos:\n'
        for i, id in enumerate(includes):
            c = ', '.join(combos[id][0])
            result += f'\t{chr(ord("a") + i)}. {id}: ({c})\n'
        result += ''
        n += 1
    return result

with open(__file__.removesuffix('.py') + '.txt', 'w') as f:
    f.write(pretty_print_combos_in_combos(combos_including_other_combos()))