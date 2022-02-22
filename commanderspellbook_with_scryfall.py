from urllib.request import urlopen, Request, quote
import pulp as pl
import json


def combos_with_scryfall_ids() -> list[set[str]]:
    result = list()

    req = Request(
        'https://api.scryfall.com/bulk-data/oracle-cards?format=json'
    )
    # Scryfall card database fetching
    card_db = dict()
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        req = Request(
            data['download_uri']
        )
        with urlopen(req) as response:
            data = json.loads(response.read().decode())
            for card in data:
                card_db[card['name'].lower().strip(' \t\n\r')] = card
                if 'card_faces' in card and len(card['card_faces']) > 1:
                    for face in card['card_faces']:
                        card_db[face['name'].lower().strip(' \t\n\r')] = card
    
    # Commander Spellbook database fetching
    req = Request(
        'https://sheets.googleapis.com/v4/spreadsheets/1KqyDRZRCgy8YgMFnY0tHSw_3jC99Z0zFvJrPbfm66vA/values:batchGet?ranges=combos!A2:Q&key=AIzaSyBD_rcme5Ff37Evxa4eW5BFQZkmTbgpHew')
    with urlopen(req) as response:
        data = json.loads(response.read().decode())
        for row in data['valueRanges'][0]['values']:
            cards = set(map(lambda name: name.lower().strip(' \t\n\r'), filter(
                lambda name: name is not None and len(name) > 0, row[1:11]))) - set([''])
            if len(cards) <= 1:
                continue
            card_ids = set()
            skipped = False
            for card in cards:
                if card not in card_db:
                    print(f'{card} is probably misspelled. Skipping combo {row[0]}.')
                    skipped = True
                    break
                card_ids.add(card_db[card]['id'])
            if not skipped:
                result.append(card_ids)
    return result

