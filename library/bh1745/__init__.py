from i2cdevice import Device, Register, BitField
from i2cdevice.adapter import LookupAdapter, U16ByteSwapAdapter

class BH1745:
    def __init__(self, i2c_addr=0x38, i2c_dev=None):
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        # Device definition
        self._bh1745 = Device([0x38, 0x39], i2c_dev=self._i2c_dev, bit_width=8, registers=(
            # Part ID should be 0b001011 or 0x0B
            Register('SYSTEM_CONTROL', 0x40, fields=(
                BitField('sw_reset',  0b10000000),
                BitField('int_reset', 0b01000000),
                BitField('part_id',   0b00111111, read_only=True)
            )),

            Register('MODE_CONTROL1', 0x41, fields=(
                BitField('measurement_time_ms', 0b00000111, adapter=LookupAdapter({160: 0b000, 320: 0b001, 640: 0b010, 1280: 0b011, 2560: 0b100, 5120: 0b101})),
            )),

            Register('MODE_CONTROL2', 0x42, fields=(
                BitField('valid',      0b10000000, read_only=True),
                BitField('rgbc_en',    0b00010000),
                BitField('adc_gain_x', 0b00000011, adapter=LookupAdapter({1: 0b00, 2: 0b01, 16: 0b10}))
            )),

            Register('MODE_CONTROL3', 0x43, fields=(
                BitField('on', 0b11111111, adapter=LookupAdapter({True: 2, False: 0})),
            )),

            Register('COLOUR_DATA', 0x50, fields=(
                BitField('red',   0xFFFF000000000000, adapter=U16ByteSwapAdapter()),
                BitField('green', 0x0000FFFF00000000, adapter=U16ByteSwapAdapter()),
                BitField('blue',  0x00000000FFFF0000, adapter=U16ByteSwapAdapter()),
                BitField('clear', 0x000000000000FFFF, adapter=U16ByteSwapAdapter())
            ), bit_width=64, read_only=True),

            Register('DINT_DATA', 0x58, fields=(
                BitField('data', 0xFFFF, adapter=U16ByteSwapAdapter()),
            ), bit_width=16),

            Register('INTERRUPT', 0x60, fields=(
                BitField('status', 0b10000000, read_only=True),
                BitField('latch',  0b00010000, adapter=LookupAdapter({0:1, 1:0})),
                BitField('source', 0b00001100, read_only=True, adapter=LookupAdapter({'red': 0b00, 'green': 0b01, 'blue': 0b10, 'clear': 0b11})),
                BitField('enable', 0b00000001)
            )),

            # 00: Interrupt status is toggled at each measurement end
            # 01: Interrupt status is updated at each measurement end
            # 10: Interrupt status is updated if 4 consecutive threshold judgements are the same
            # 11: Blah blah ditto above except for 8 consecutive judgements
            Register('PERSISTENCE', 0x61, fields=(
                BitField('mode', 0b00000011, adapter=LookupAdapter({'toggle': 0b00, 'update': 0b01, 'update_on_4': 0b10, 'update_on_8': 0b11})),
            )),

            # High threshold defaults to 0xFFFF
            # Low threshold defaults to 0x0000
            Register('THRESHOLD', 0x62, fields=(
                BitField('high', 0xFFFF0000, adapter=U16ByteSwapAdapter()),
                BitField('low',  0x0000FFFF, adapter=U16ByteSwapAdapter())
            ), bit_width=32),

            # Default MANUFACTURER ID is 0xE0h
            Register('MANUFACTURER', 0x92, fields=(
                BitField('id', 0xFF),    
            ), read_only=True, volatile=False)
        ))

        self._bh1745.select_address(self._i2c_addr)

        # TODO : Integrate into i2cdevice so that LookupAdapter fields can always be exported to constants
        # Iterate through all register fields and export their lookup tables to constants
        for register in self._bh1745.registers:
            register = self._bh1745.registers[register]
            for field in register.fields:
                field = register.fields[field]
                if isinstance(field.adapter, LookupAdapter):
                    for key in field.adapter.lookup_table:
                        value = field.adapter.lookup_table[key]
                        name = "BH1745_{register}_{field}_{key}".format(
                                    register=register.name,
                                    field=field.name,
                                    key=key
                                ).upper()
                        globals()[name] = key


        """
        Approximate compensation for the spectral response performance curves
        """
        self._channel_compensation = (2.2, 1.0, 1.8, 10.0)
        self._enable_channel_compensation = True

    # Public API methods
    def setup(self):
        try:
            self._bh1745.SYSTEM_CONTROL.get_part_id()
        except IOError:
            raise RuntimeError("BH1745 not found: IO error attempting to query device!")

        if self._bh1745.SYSTEM_CONTROL.get_part_id() != 0b001011 or self._bh1745.MANUFACTURER.get_id() != 0xE0:
            raise RuntimeError("BH1745 not found: Manufacturer or Part ID mismatch!")

        self._bh1745.SYSTEM_CONTROL.set_sw_reset(1)

        while True:
            reset = self._bh1745.SYSTEM_CONTROL.get_sw_reset()
            if not reset:
                break
            time.sleep(0.1)

        self._bh1745.SYSTEM_CONTROL.set_int_reset(0)
        self._bh1745.MODE_CONTROL1.set_measurement_time_ms(BH1745_MODE_CONTROL1_MEASUREMENT_TIME_MS_320)
        self._bh1745.MODE_CONTROL2.set_adc_gain_x(BH1745_MODE_CONTROL2_ADC_GAIN_X_1)
        self._bh1745.MODE_CONTROL2.set_rgbc_en(1)
        self._bh1745.MODE_CONTROL3.set_on(1)

        with self._bh1745.THRESHOLD as THRESHOLD:
            THRESHOLD.set_low(0xFFFF)
            THRESHOLD.set_high(0x0000)
            THRESHOLD.write()

        self._bh1745.INTERRUPT.set_latch(1)

    def set_measurement_time_ms(self, time_ms):
        """Set the measurement time in milliseconds.

        :param time_ms: The time in milliseconds: 160, 320, 640, 1280, 2560, 5120

        """

        self._bh1745.MODE_CONTROL1.set_measurement_time_ms(time_ms)

    def set_adc_gain_x(self, gain_x):
        """Set the ADC gain multiplier.
        
        :param gain_x: Must be either 1, 2 or 16

        """

        self._bh1745.MODE_CONTROL2.set_adc_gain_x(gain_x)

    def set_leds(self, state):
        """Toggle the onboard LEDs.
        
        :param state: Either 1 for on, or 0 for off
        
        """

        self._bh1745.INTERRUPT.set_enable(1 if state else 0)

    def set_channel_compensation(self, r, g, b, c):
        """Set the channel compensation scale factors.
        
        :param r: multiplier for red channel
        :param g: multiplier for green channel
        :param b: multiplier for blue channel
        :param c: multiplier for clear channel

        If you intend to measure a particular class of objects, say a set of matching wooden blocks with similar reflectivity and paint finish
        you should calibrate the channel compensation until you see colour values that broadly represent the colour of the objects you're testing.

        The default values were derived by testing a set of 5 Red, Green, Blue, Yellow and Orange wooden blocks.

        These scale factors are applied in `get_rgbc_raw` right after the raw values are read from the sensor.

        """

        self._channel_compensation = (r, g, b, c)

    def enable_white_balance(self, enable):
        """Enable scale compensation for the channels.

        :param enable: True to enable, False to disable

        See: `set_channel_compensation` for details.

        """

        self._enable_channel_compensation = True if enable else False

    def get_rgbc_raw(self):
        """Return the raw Red, Green, Blue and Clear readings"""

        with self._bh1745.COLOUR_DATA as COLOUR_DATA:
            r, g, b, c = COLOUR_DATA.get_red(), COLOUR_DATA.get_green(), COLOUR_DATA.get_blue(), COLOUR_DATA.get_clear()

        if self._enable_channel_compensation:
            cr, cg, cb, cc = self._channel_compensation
            r, g, b, c = r*cr, g*cg, b*cb, c*cc

        return (r, g, b, c)

    def get_rgb_clamped(self):
        """Return an RGB value scaled against max(r, g, b)

        This will clamp/saturate one of the colour channels, providing a clearer idea
        of what primary colour an object is most likely to be.

        However the resulting colour reading will not be accurate for other purposes.

        """

        r, g, b, c = self.get_rgbc_raw()

        div = max(r, g, b)

        if div > 0:
            r, g, b = [int((x / float(div)) * 255) for x in (r, g, b)]
            return (r, g, b)

        return (0, 0, 0)

    def get_rgb_scaled(self):
        """Return an RGB value scaled against the clear channel"""

        r, g, b, c = self.get_rgbc_raw()

        if c > 0:
            r, g, b = [min(255,int((x / float(c)) * 255)) for x in (r, g, b)]
            return (r, g, b)

        return (0, 0, 0)

