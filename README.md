# Commander Spellbook Tools
Is an experiment sandbox that exploits the commander spellbook combos database and JSON API with Python in order to generate knowledge.

## Combos including other combos
The file `combos_including_other_combos.py` provides methods to find combos including other combos, which are somewhat redundant.

## Missing combos by card effect variants
The file `missing_combos_by_variants.py` provides methods to find new combos, absent from commander spellbook, based on a dataset of card replacements, callend _variants_.
Example of a replacement: _Carrion Feeder_ with _Viscera Seer_.

It also provides a questionable, fuzzy algorithm that generates a list of variants based on the assumption that if a card can be replaced by a set of some other cards there will be combos in the database (at least _n_, found empirically) where the first card is actually replaced by the set.

## CommanderSpellbook + Scryfall
The file `commanderspellbook_with_scryfall.py` provides utilities to generate a conjunct dataset between Scryfall and Commander Spellbook.
