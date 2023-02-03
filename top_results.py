
from collections import defaultdict
import json
from urllib.request import Request, urlopen


def results() -> dict[str, int]:
    results = defaultdict(int)
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
            for effect in pros:
                results[effect] += 1
    return results

for result, times in sorted(filter(lambda i: i[1] > 5, results().items()), key=lambda item: item[1], reverse=True):
    print(f'{result}: {times}')