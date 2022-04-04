
from collections import defaultdict
import json
from urllib.request import Request, urlopen
import statistics

def find_card_variants() -> dict[str, frozenset[frozenset[str]]]:
    combo_db = list[set]()
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
            combo_db.append(cards)
    
    variants = defaultdict(list)
    for combo in combo_db:
        for card in combo:
            combo_variant_query = combo - frozenset([card])
            for possible_variant in combo_db:
                if combo_variant_query.issubset(possible_variant):
                    card_variant = possible_variant - combo_variant_query
                    if len(card_variant) == 0:
                        #print(f'{possible_variant} is a combo subset of {combo}')
                        continue
                    if card in card_variant:
                        continue
                    if len(combo_variant_query) >= len(card_variant):
                        variants[card].append(card_variant)

    result = dict[str, frozenset[frozenset[str]]]()
    for card, vs in variants.items():
        combo_count = sum(1 if card in combo else 0 for combo in combo_db)
        vsf = frozenset([v for v in vs if vs.count(v) > combo_count / 3 and not any([c.issubset(v) for c in vs if c != v])])
        if len(vsf) > 0:
            result[card] = vsf
    return result

def find_missing_combos(variants: dict[str, frozenset[frozenset[str]]]) -> dict[frozenset[str], set[frozenset[str]]]:
    combo_db = list[frozenset]()
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
            combo_db.append(cards)
    
    missing_combos = defaultdict(set)
    for combo in combo_db:
        for variant_name, variant_options in variants.items():
            if variant_name in combo:
                for variant in variant_options:
                    new_combo = combo - frozenset([variant_name]) | variant
                    if new_combo not in combo_db and all([new_combo not in new_combos for new_combos in missing_combos.values()]):
                        missing_combos[combo].add(new_combo)
    return missing_combos

def pretty_print_all_combo_replacements(missing_combos: dict[frozenset[str], set[frozenset[str]]]) -> str:
    result = ''
    for combo, combos in missing_combos.items():
        combo_name = ' + '.join(sorted(combo))
        result += f'The combo "{combo_name}" is missing the following variants:\n'
        for combo in combos:
            result += f'\t{" + ".join(sorted(combo))}\n'
    return result


def pretty_print_all_combo_suggestions(missing_combos: dict[frozenset[str], set[frozenset[str]]]) -> str:
    result = ''
    u = defaultdict(int)
    for new_combos in missing_combos.values():
        for new_combo in new_combos:
            u[new_combo] += 1
    for new_combo in sorted(u.keys(), key=lambda combo: str(combo)):
        result += f'Combo suggestion: {" + ".join(new_combo)}\n'
    return result


