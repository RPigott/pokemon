import numpy as np
import pandas as pd
import struct


class GARCFile:
    magic = b'CRAG'
    text_base_key = 0x7c89
    text_adv_key  = 0x2983

    @staticmethod
    def key_sequence(key):
        while True:
            yield key
            key = ((key << 3) & 0xffff) | (key >> 13)

    def __init__(self, filename):
        self.filename = filename
        self.record_descriptors = []
        self._set_offsets()
    
    def _set_offsets(self):
        with open(self.filename, 'rb') as file:
            magic = file.read(0x04)
            if magic != self.magic:
                raise ValueError("Invalid GARC magic {}. Expected {}".format(magic, self.magic))

            self.fato_offset, = struct.unpack('<I', file.read(0x04))
            
            file.seek(self.fato_offset)
            fato_hdr = file.read(0x04)
            if fato_hdr != b'OTAF':
                raise IOError("FATO out of place at 0x{:x}, found {}.".format(self.fato_offset, fato_hdr))
            
            self.fatb_offset, = struct.unpack('<I', file.read(0x04))
            self.fatb_offset = self.fato_offset + self.fatb_offset
            
            file.seek(self.fatb_offset)
            fatb_hdr = file.read(0x04)
            if fatb_hdr != b'BTAF':
                raise IOError("FATB out of place at 0x{:x}, found {}.".format(self.fatb_offset, fatb_hdr))

            self.fimb_offset, self.n_records = struct.unpack('<2I', file.read(0x08))
            self.fimb_offset = self.fatb_offset + self.fimb_offset

            for n in range(self.n_records):
                _, start, stop, size, _, _ = struct.unpack('<3IHBB', file.read(0x10))
                self.record_descriptors.append((start, size))

            file.seek(self.fimb_offset)
            fimb_hdr = file.read(0x04)
            if fimb_hdr != b'BMIF':
                raise IOError("BMIF out of place at 0x{:x}, found {}".format(self.fimb_offset, fimb_hdr))
            record_offset, = struct.unpack('<H', file.read(0x02))
            self.data_segment_offset = self.fimb_offset + record_offset

    def record_iterator(self):
        with open(self.filename, 'rb') as file:
            file.seek(self.data_segment_offset)
            for offset, size in self.record_descriptors:
                file.seek(self.data_segment_offset + offset)
                yield file.read(size)

    def mini_iterator(self, n):
        offset, size = self.record_descriptors[n]
        with open(self.filename, 'rb') as file:
            data_base_offset = self.data_segment_offset + offset
            file.seek(data_base_offset)
            size, length = struct.unpack('<2H', file.read(0x04))
            mini_offsets = []
            for r in range(length + 1):
                mini_offset, _ = struct.unpack('<2H', file.read(0x04))
                mini_offsets.append(mini_offset)
            for r in range(length):
                # file.seek(data_base_offset + mini_offset) # contiguous?
                yield file.read(mini_offsets[r + 1] - mini_offsets[r])

    def text_iterator(self, n):
        start, size = self.record_descriptors[n]
        with open(self.filename, 'rb') as file:
            file.seek(self.data_segment_offset + start)
            _, n_records, total_length, _, _ = struct.unpack('<2H3I', file.read(0x10))
            total_length = struct.unpack('<I', file.read(0x4))

            enc_offsets = []
            for n in range(n_records):
                offset, length, _ = struct.unpack('<I2H', file.read(0x8))
                enc_offsets.append((offset, length))

            data_base_offset = self.data_segment_offset + start + 0x10
            key = self.text_base_key
            for offset, length in enc_offsets:
                file.seek(data_base_offset + offset) # Not guaranteed to be adjacent
                shorts = struct.unpack(f'<{length}H', file.read(2*length))
                keys = self.key_sequence(key)
                text = ''.join(chr(c ^ key) for c, key in zip(shorts, keys)).strip("\x00")
                # Correct some symbols
                text = text.translate({
                            0xe08f: '♀',
                            0xe08e: '♂'
                        })
                yield text
                key = (key + self.text_adv_key) & 0xffff




from collections import namedtuple

Field = namedtuple('Field', ['identifier', 'offset', 'format', 'transform', 'packed'])

def replace(transform):
    def _transform(item):
        return transform[item] if item in transform else item
    return _transform

def fill_none(item):
    return None if item is 0 else item

def split_field(form, width):
    size = struct.calcsize(form)
    def _transform(bs):
        result = []
        mask = (1 << width) - 1
        for idx in range(8*size // width):
            shift = width * idx
            value = (bs & (mask << shift)) >> shift
            result.append(value)
        return result
    return _transform

def fields_to_fmt(fields):
    fmt = '<' # little endian
    offset = 0x00
    for field in fields:
        disp = field.offset - offset
        fmt += f'{disp}x{field.format}'
        offset = field.offset + struct.calcsize(field.format)
    return fmt

def to_record(fields, record):
    fmt = fields_to_fmt(fields)
    data = struct.unpack(fmt, record)
    d = {}
    for field, value in zip(fields, data):
        if field.identifier is None:
            continue
        
        if field.packed:
            d.update({name: mini for name, mini in zip(field.identifier, field.transform(value))
                if name is not None})
        else:
            d[field.identifier] = field.transform(value) if field.transform else value
    return d
        

record_descriptors = {
        'personal': [
                Field('hp'    , 0x00, 'B', None, False),
                Field('atk'   , 0x01, 'B', None, False),
                Field('def'   , 0x02, 'B', None, False),
                Field('spe'   , 0x03, 'B', None, False),
                Field('spa'   , 0x04, 'B', None, False),
                Field('spd'   , 0x05, 'B', None, False),
                Field('type1' , 0x06, 'B', None, False),
                Field('type2' , 0x07, 'B', None, False),
                Field('capture_rate', 0x08, 'B', None, False),
                Field('stage' , 0x09, 'B', None, False),
                Field(
                    ['ev_hp', 'ev_atk', 'ev_def', 'ev_spe', 'ev_spa', 'ev_spd', None, None],
                    0x0a,
                    'H',
                    split_field('H', 2),
                    True
                ),
                Field('item1' , 0x0c, 'H', fill_none, False),
                Field('item2' , 0x0e, 'H', fill_none, False),
                Field('item3' , 0x10, 'H', fill_none, False),
                Field('gender_rate', 0x12, 'B', None, False),
                Field('hatch_cycles', 0x13, 'B', None, False),
                Field('base_happiness', 0x14, 'B', None, False),
                Field('exp_group', 0x15, 'B', replace({
                		0x00: 'Medium Fast',
                		0x01: 'Erratic',
                		0x02: 'Fluctuating',
                		0x03: 'Medium Slow',
                		0x04: 'Fast',
                		0x05: 'Slow'
                    }), False),
                Field('egg_group1', 0x16, 'B', None, False),
                Field('egg_group2', 0x17, 'B', None, False),
                Field('ability1', 0x18, 'B', None, False),
                Field('ability2', 0x19, 'B', None, False),
                Field('ability_hidden', 0x1a, 'B', None, False),
                Field('escape_rate', 0x1b, 'B', None, False),
                Field('alt_id', 0x1c, 'I', fill_none, False),
                Field('multiplicity', 0x20, 'B', None, False),
                Field('color', 0x21, 'B', replace({
                        0x00: 'Red',
                        0x01: 'Blue',
                        0x02: 'Yellow',
                        0x03: 'Green',
                        0x04: 'Black',
                        0x05: 'Brown',
                        0x06: 'Purple',
                        0x07: 'Gray',
                        0x08: 'White',
                        0x09: 'Pink'
                    }), False),
                Field('base_exp', 0x22, 'H', None, False),
                Field('height', 0x24, 'H', lambda h: h / 100, False),
                Field('weight', 0x26, 'H', lambda w: w / 10, False),
                Field(None, 0x28, '16s', None, False), # TMs
                Field(None, 0x38, '4s', None, False), # special tutors
                Field(None, 0x3c, '16s', None, False), # Move tutor
                Field(None, 0x4c, '6s', None, False), # Z-move?
                Field('local_variant', 0x52, 'B', lambda lv: True if lv is 1 else False, False),
                Field(None, 0x53, 's', None, False) # empty
            ],

            'move': [
                Field('type', 0x00, 'B', None, False),
                # Field('style', 0x01, 'B', None, False),
                Field('category', 0x02, 'B', replace({0: 'Status', 1: 'Physical', 2: 'Special'}), False),
                Field('power', 0x03, 'B', replace({0: None}), False),
                Field('accuracy', 0x04, 'B', replace({101: None}), False),
                Field('pp', 0x05, 'B', None, False),
                Field('priority', 0x06, 'b', None, False),
                # Field((None, None), 0x07, 'B', None, True), # min/max hits
                Field('effect', 0x08, 'H', None, False),
                Field('effect_chance', 0x0a, 'B', None, False),
                Field('effect_min_turns', 0x0b, 'B', None, False),
                Field('effect_max_turns', 0x0c, 'B', None, False),
                Field(None, 0x0d, 'B', None, False), # ??
                Field('crit_chance', 0x0e, 'B', None, False),
                Field('flinch_chance', 0x0f, 'B', None, False),
                Field(['drain', 'recoil'], 0x12, 'b', lambda rd: (rd, 0) if rd > 0 else (0, -rd), True),
                Field(['heal', 'damage'], 0x13, 'b', lambda hd: (hd, 0) if hd > 0 else (0, -hd), True),
                Field('stat1', 0x15, 'B', None, False),
                Field('stat2', 0x16, 'B', None, False),
                Field('stat3', 0x17, 'B', None, False),
                Field('stat1_num', 0x18, 'B', None, False),
                Field('stat2_num', 0x19, 'B', None, False),
                Field('stat3_num', 0x1a, 'B', None, False),
                Field('stat1_chance', 0x1b, 'B', None, False),
                Field('stat2_chance', 0x1c, 'B', None, False),
                Field('stat3_chance', 0x1d, 'B', None, False),
                Field('dance', 0x26, 'B', lambda d: True if d is 1 else False, False),
                Field(None, 0x27, 'B', None, False) # empty
            ],
}


from itertools import zip_longest
personal = GARCFile('game/romfs/a/0/1/7')
text = GARCFile('game/romfs/a/0/3/2')
dsrc = filter(lambda val: len(val) == 0x54, personal.record_iterator())

def pad_itr(itr, value, max_len):
    for n, item in zip_longest(range(max_len), itr, fillvalue = value):
        yield item

df = pd.DataFrame.from_records([to_record(record_descriptors['personal'], d) for d in dsrc])
df['name'] = list(text.text_iterator(60)) + [''] * (df.shape[0] - 808)
df['form'] = list(text.text_iterator(119))[df.shape[0]]

