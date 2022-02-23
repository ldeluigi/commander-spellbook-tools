from collections import defaultdict
from math import comb
from unittest import result
from urllib.request import urlopen, Request, quote
import pulp as pl
import json

def combos_including_other_combos(pool: set[frozenset[str]]) -> dict[frozenset[str], set[frozenset[int]]]:
    combo_db = pool
    result = defaultdict(set)
    for combo in combo_db:
        for other in combo_db:
            if other.issubset(combo) and combo != other:
                result[combo].add(other)
    return result

def separate_enablers() -> dict[str, tuple[set[frozenset[str]]], set[frozenset[str]]]:
    combosdb = dict[frozenset[str], frozenset[str]]()    
    # Commander Spellbook database fetching
    req = Request(
        'https://sheets.googleapis.com/v4/spreadsheets/1KqyDRZRCgy8YgMFnY0tHSw_3jC99Z0zFvJrPbfm66vA/values:batchGet?ranges=combos!A2:Q&key=AIzaSyBD_rcme5Ff37Evxa4eW5BFQZkmTbgpHew')
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        for row in data['valueRanges'][0]['values']:
            cards = frozenset(map(lambda name: name.lower().strip(' \t\n\r'), filter(
                lambda name: name is not None and len(name) > 0, row[1:11]))) - set([''])
            if len(cards) <= 1:
                continue
            pros = [token.replace('.', '') for token in row[14].lower().strip(' \t\n\r').split('. ')]
            combosdb[cards] = frozenset(pros)
    combos_by_pro = defaultdict[str, set[frozenset[str]]](set)
    for combo in combosdb:
        for pro in combosdb[combo]:
            combos_by_pro[pro].add(combo)
    
    enablers_by_pro = defaultdict[str, set[frozenset[str]]](set)
    
    for pro, combos in combos_by_pro.items():
        if len(combos_by_pro[pro]) <= 1:
            continue
        combos_including_combos = combos_including_other_combos(combos)
        for combo, included_combos in combos_including_combos.items():
            for included_combo in included_combos:
                if not any([e.issubset(included_combo) for e in enablers_by_pro[pro]]):
                    enablers_by_pro[pro].difference_update([e for e in enablers_by_pro[pro] if included_combo.issubset(e)])
                    enablers_by_pro[pro].add(included_combo)
    
    pros_by_enabler = defaultdict[frozenset[str], set[str]](set)
    for pro, enablers in enablers_by_pro.items():
        for enabler in enablers:
            pros_by_enabler[enabler].add(pro)
    
    outlets_by_pro = defaultdict[str, set[frozenset[str]]](set)
    for combo, pros in combosdb.items():
        for enabler, epros in pros_by_enabler.items():
            added_pros = pros - epros
            possible_outlet = combo - enabler
            if enabler.issubset(combo) and len(added_pros) > 0 and len(possible_outlet) > 0 and not any([possible_outlet.issubset(enabler) for enabler in enablers_by_pro[pro]]):
                for pro in epros:
                    outlets_by_pro[pro].add(possible_outlet)

    result = dict[str, tuple[set[frozenset[str]]], set[frozenset[str]]]()
    for pro in outlets_by_pro | enablers_by_pro:
        result[pro] = (enablers_by_pro[pro] if pro in enablers_by_pro else set(), outlets_by_pro[pro] if pro in outlets_by_pro else set())
    
    return result

def pretty_print_by_pro(pros_to_tuple: dict[str, tuple[set[frozenset[str]]], set[frozenset[str]]]):
    result = ''
    for pro, (enablers, outlets) in sorted(pros_to_tuple.items(), key=lambda x: x[0]):
        if len(enablers) > 0:
            result += f'For {pro}:\n'
            result += f'\tEnablers:\n'
            for enabler in sorted(enablers, key=str):
                result += f'\t\t{" + ".join(enabler)}\n'
        if len(outlets) > 0:
            result += f'\tOutlets:\n'
            for outlet in sorted(outlets, key=str):
                result += f'\t\t{" + ".join(outlet)}\n'
    return result

print(pretty_print_by_pro(separate_enablers()))