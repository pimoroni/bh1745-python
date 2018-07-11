from .device import _mask_width, _byte_swap, _leading_zeros, _trailing_zeros, _unmask, _mask, Device, Register, BitField

bh1745 = Device(0x38, bitwidth=8)

"""
Part ID should be 0b001011 or 0x0B
"""
SYSTEM_CONTROL = Register(bh1745, 0x40, fields=(
    BitField('sw_reset',  0b10000000),
    BitField('int_reset', 0b010000000),
    BitField('part_id',   0b00111111, read_only=True)
))

MODE_CONTROL1 = Register(bh1745, 0x41, fields=(
    BitField('measurement_time_ms', 0b00000111, values_map={160: 0b000, 320: 0b001, 640: 0b010, 1280: 0b011, 2560: 0b100, 5120: 0b101}),
))

MODE_CONTROL2 = Register(bh1745, 0x42, fields=(
    BitField('valid',      0b10000000, read_only=True),
    BitField('rgbc_en',    0b00010000),
    BitField('adc_gain_x', 0b00000011, values_map={1: 0b00, 2: 0b01, 16: 0b10})
))

MODE_CONTROL3 = Register(bh1745, 0x43, fields=(
    BitField('on', 0b11111111, values_map={True: 2, False: 0}),
))

COLOUR_DATA = Register(bh1745, 0x50, fields=(
    BitField('red',   0xFFFF000000000000, values_in=_byte_swap, values_out=_byte_swap),
    BitField('green', 0x0000FFFF00000000, values_in=_byte_swap, values_out=_byte_swap),
    BitField('blue',  0x00000000FFFF0000, values_in=_byte_swap, values_out=_byte_swap),
    BitField('clear', 0x000000000000FFFF, values_in=_byte_swap, values_out=_byte_swap)
), bitwidth=64, read_only=True)

DINT_DATA = Register(bh1745, 0x58, fields=(
    BitField('data', 0xFFFF, values_in=_byte_swap, values_out=_byte_swap),
), bitwidth=16)

INTERRUPT = Register(bh1745, 0x60, fields=(
    BitField('status', 0b10000000, read_only=True),
    BitField('latch',  0b00010000, values_map={0:1, 1:0}),
    BitField('source', 0b00001100, read_only=True, values_map={'red': 0b00, 'green': 0b01, 'blue': 0b10, 'clear': 0b11}),
    BitField('enable', 0b00000001)
))

"""
00: Interrupt status is toggled at each measurement end
01: Interrupt status is updated at each measurement end
10: Interrupt status is updated if 4 consecutive threshold judgements are the same
11: Blah blah ditto above except for 8 consecutive judgements
"""
PERSISTENCE = Register(bh1745, 0x61, fields=(
    BitField('mode', 0b00000011, values_map={'toggle': 0b00, 'update': 0b01, 'update_on_4': 0b10, 'update_on_8': 0b11}),
))


"""
High threshold defaults to 0xFFFF
Low threshold defaults to 0x0000
"""
THRESHOLD = Register(bh1745, 0x62, fields=(
    BitField('high', 0xFFFF0000, values_in=_byte_swap, values_out=_byte_swap),
    BitField('low',  0x0000FFFF, values_in=_byte_swap, values_out=_byte_swap)
), bitwidth=32)

"""
Default value is 0xE0h
"""
MANUFACTURER = Register(bh1745, 0x92, fields=(
    BitField('id', 0xFF),    
), read_only=True, volatile=False)
