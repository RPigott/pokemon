import numpy as np
import pandas as pd
import struct

from util import *
from sqlalchemy import create_engine

files = {
            'move': 'game/romfs/a/0/1/1',
            'egg_move': 'game/romfs/a/0/1/2',
            'levelup_move': 'game/romfs/a/0/1/3',
            'evolution': 'game/romfs/a/0/1/4',
            'mega_evolution': 'game/romfs/a/0/1/5',
            'personal': 'game/romfs/a/0/1/7',
            'item': 'game/romfs/a/0/1/9',
            'text_jp': 'game/romfs/a/0/3/0',
            'text_jk': 'game/romfs/a/0/3/1',
            'text_en': 'game/romfs/a/0/3/2',
            'text_fr': 'game/romfs/a/0/3/3',
            'text_it': 'game/romfs/a/0/3/4',
            'text_gr': 'game/romfs/a/0/3/5',
            'text_es': 'game/romfs/a/0/3/6',
            'text_kr': 'game/romfs/a/0/3/7',
            'text_ct': 'game/romfs/a/0/3/8',
            'text_cs': 'game/romfs/a/0/3/9'

        }

text_refs = {
            "item_flavor": 39,
            "item_names": 40,
            "species_names": 60,
            "metlist_000000": 72,
            "battle_royal_names": 91,
            "natures": 92,
            "ability_names": 101,
            "battle_tree_names": 104,
            "trainer_text": 109,
            "trainer_names": 110,
            "trainer_classes": 111,
            "type_names": 112,
            "move_flavor": 117,
            "move_names": 118,
            "form_names": 119,
            "species_classifications": 121,
            "pokedex_1": 124,
            "pokedex_2": 125
        }

game_text = {
    'name_en': GARCFile(files['text_en']),
    'name_jp': GARCFile(files['text_jp']),
    'name_fr': GARCFile(files['text_fr']),
    'name_gr': GARCFile(files['text_gr'])
}

def make_text_table(target):
    return pd.DataFrame({
        lang: list(src.text_iterator(target))
        for lang, src in game_text.items()
        })

def flag_field(bts, n):
    checks = []
    ints = list(b for b, in struct.iter_unpack('<B', bts))
    for k in range(n):
        idx, sft = divmod(k, 8)
        check = ints[idx] & (1 << sft) > 0
        if check:
            checks.append(k + 1)
    return checks

engine = create_engine('postgres://ronan@localhost/pokemon')

# Personal
personal = GARCFile(files['personal'])
dsrc = filter(lambda r: len(r) == 0x54, personal.record_iterator()) # weird final record
fields = record_descriptors['personal']
df_personal = pd.DataFrame.from_records([to_record(fields, data) for data in dsrc])

# correct type2 duplication
df_personal.loc[df_personal['type2'] == df_personal['type1'], 'type2'] = None

# species names
df_species_names = make_text_table(text_refs['species_names'])
df_personal = df_personal.join(df_species_names)
df_form_names = make_text_table(text_refs['form_names'])

# df_personal.to_sql('species', engine, if_exists = 'append', index_label = 'id')
# df_form_names.to_sql('forms', engine, if_exists = 'append', index_label = 'id')

# Moves
moves = GARCFile(files['move'])
dsrc = moves.mini_iterator(0)
fields = record_descriptors['move']
df_moves = pd.DataFrame.from_records([to_record(fields, data) for data in dsrc])
df_move_names = make_text_table(text_refs['move_names'])
df_moves = df_moves.join(df_move_names)

# df_moves.to_sql('moves', engine, if_exists = 'append', index_label = 'id')

# Levelup
levelup = GARCFile(files['levelup_move'])
records = []
for idx, data in enumerate(levelup.record_iterator()):
    for move, level in struct.iter_unpack('<HH', data):
        if move == level == 0xffff:
            break
        records.append({'species': idx, 'move': move, 'level': level})
df_levelup = pd.DataFrame.from_records(records)

# df_levelup.to_sql('levelup', engine, if_exists = 'append', index = False)

# Egg move
egg_move = GARCFile(files['egg_move'])
records = []
for idx, data in enumerate(egg_move.record_iterator()):
    for move, in struct.iter_unpack('<H', data[4:]):
        records.append({'species': idx, 'move': move})

df_egg_move = pd.DataFrame.from_records(records)
# df_egg_move.to_sql('egg_moves', engine, if_exists = 'append', index = False)

# Evolution
evolution = GARCFile(files['evolution'])
records = []
for idx, bts in enumerate(evolution.record_iterator()):
    for k in range(0, len(bts), 0x08):
        evo = bts[k:k+0x08]
        method, aux, target, form, level = struct.unpack('<3H2B', evo)
        if method:
            records.append({
                    'species': idx,
                    'method': method,
                    'auxiliary': aux,
                    'target': target,
                    'target_form': form,
                    'level': level
                })
df_evolution = pd.DataFrame.from_records(records)
# df_evolution.to_sql('evolution', engine, if_exists = 'append', index_label = 'id')

df_ability_names = make_text_table(text_refs['ability_names'])
# df_ability_names.to_sql('abilities', engine, if_exists = 'append', index_label = 'id')

df_type_names = make_text_table(text_refs['type_names'])
# df_type_names.to_sql('types', engine, if_exists = 'append', index_label = 'id')

df_item_names = make_text_table(text_refs['item_names'])
# df_item_names.to_sql('items', engine, if_exists = 'append', index_label = 'id')

# 0x5bb98e
tms = [
	0, 526, 337, 473, 347, 46, 92, 258, 339, 474, 237, 241, 269, 58, 59, 63, 113, 182, 240,
        355, 219, 218, 76, 479, 85, 87, 89, 216, 141, 94, 247, 280, 104, 115, 482, 53, 188, 201,
        126, 317, 332, 259, 263, 488, 156, 213, 168, 490, 496, 497, 315, 211, 411, 412, 206, 503,
        374, 451, 507, 693, 511, 261, 512, 373, 153, 421, 371, 684, 416, 397, 694, 444, 521, 86,
        360, 14, 19, 244, 523, 524, 157, 404, 525, 611, 398, 138, 447, 207, 214, 369, 164, 430,
        433, 528, 57, 555, 267, 399, 127, 605, 590
]

# 0x5d9a7c old?
# 0x5e6860
tutor = [
          450, 343, 162, 530, 324, 442, 402, 529, 340, 67, 441, 253, 9, 7, 8, 277, 335,
          414, 492, 356, 393, 334, 387, 276, 527, 196, 401, 428, 406, 304, 231, 20, 173,
          282, 235, 257, 272, 215, 366, 143, 220, 202, 409, 264, 351, 352, 380, 388, 180,
          495, 270, 271, 478, 472, 283, 200, 278, 289, 446, 285, 477, 502, 432, 710, 707,
          675, 673
]


df_tms = pd.DataFrame({'move': tms})
# df_tms.to_sql('tm_moves', engine, index_label = 'id')

df_tutor = pd.DataFrame({'move': tutor}, index = np.arange(len(tutor)))
# df_tutor.to_sql('tutor_moves', engine, index_label = 'id')

def check(bts, n):
    a, b = divmod(n, 8)
    return bts[a] & (1 << b) > 0

def checks(size, bts):
    size = struct.calcsize(size) * 8
    return filter(lambda n: check(bts, n), range(size))

dsrc = filter(lambda d: len(d) == 0x54, personal.record_iterator())
tm_records = []
tutor_records = []
for idx, data in enumerate(dsrc):
    tm_bts = data[0x28:0x38]
    tutor_bts = data[0x3c:0x4c]
    for c in flag_field(tm_bts, 100):
        tm_records.append({'species': idx, 'tm': c})
    for c in checks('<16B', tutor_bts):
        tutor_records.append({'species': idx, 'tutor': c})

df_tm_learnset = pd.DataFrame.from_records(tm_records)
# df_tm_learnset.to_sql('tm_learnset', engine, index = False)

df_tutor_learnset = pd.DataFrame.from_records(tutor_records)
# df_tutor_learnset.to_sql('tutor_learnset', engine, index = False)

# df_dex1 = make_text_table(text_refs['pokedex_1'])
# df_dex2 = make_text_table(text_refs['pokedex_2'])
# df_classification = make_text_table(text_refs['species_classifications'])

if __name__ == '__main__':
    df_ability_names.to_sql('abilities', engine, if_exists = 'append', index_label = 'id')
    df_item_names.to_sql('items', engine, if_exists = 'append', index_label = 'id')
    df_type_names.to_sql('types', engine, if_exists = 'append', index_label = 'id')
    df_personal.to_sql('species', engine, if_exists = 'append', index_label = 'id') # species
    df_form_names.to_sql('forms', engine, if_exists = 'append', index_label = 'id')
    df_evolution.to_sql('evolution', engine, if_exists = 'append', index_label = 'id')
    df_moves.to_sql('moves', engine, if_exists = 'append', index_label = 'id')
    df_levelup.to_sql('levelup', engine, if_exists = 'append', index = False)
    df_egg_move.to_sql('egg_moves', engine, if_exists = 'append', index = False)
    df_tms.to_sql('tm_moves', engine, index_label = 'id')
    df_tutor.to_sql('tutor_moves', engine, index_label = 'id')
    df_tm_learnset.to_sql('tm_learnset', engine, index = False)
    df_tutor_learnset.to_sql('tutor_learnset', engine, index = False)
    # df_classification.to_sql('species_class', engine, index_label = 'id')
