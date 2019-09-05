"""Library for the BH1745 colour sensor."""
import time

from i2cdevice import Device, Register, BitField
from i2cdevice.adapter import LookupAdapter, U16ByteSwapAdapter


__version__ = '0.0.4'

I2C_ADDRESSES = [0x38, 0x39]
BH1745_RESET_TIMEOUT_SEC = 2


class BH1745TimeoutError(Exception):  # noqa D101
    pass


class BH1745:
    """BH1745 colour sensor."""

    def __init__(self, i2c_addr=0x38, i2c_dev=None):
        """Initialise sensor.

        :param i2c_addr: i2c address of sensor
        :param i2c_dev: SMBus-compatible instance

        """
        self._i2c_addr = i2c_addr
        self._i2c_dev = i2c_dev
        self._is_setup = False
        # Device definition
        self._bh1745 = Device(I2C_ADDRESSES, i2c_dev=self._i2c_dev, bit_width=8, registers=(
            # Part ID should be 0b001011 or 0x0B
            Register('SYSTEM_CONTROL', 0x40, fields=(
                BitField('sw_reset', 0b10000000),
                BitField('int_reset', 0b01000000),
                BitField('part_id', 0b00111111, read_only=True)
            )),

            Register('MODE_CONTROL1', 0x41, fields=(
                BitField('measurement_time_ms', 0b00000111, adapter=LookupAdapter({
                    160: 0b000,
                    320: 0b001,
                    640: 0b010,
                    1280: 0b011,
                    2560: 0b100,
                    5120: 0b101
                })),
            )),

            Register('MODE_CONTROL2', 0x42, fields=(
                BitField('valid', 0b10000000, read_only=True),
                BitField('rgbc_en', 0b00010000),
                BitField('adc_gain_x', 0b00000011, adapter=LookupAdapter({
                    1: 0b00, 2: 0b01, 16: 0b10}))
            )),

            Register('MODE_CONTROL3', 0x44, fields=(
                BitField('on', 0b11111111, adapter=LookupAdapter({True: 2, False: 0})),
            )),

            Register('COLOUR_DATA', 0x50, fields=(
                BitField('red', 0xFFFF000000000000, adapter=U16ByteSwapAdapter()),
                BitField('green', 0x0000FFFF00000000, adapter=U16ByteSwapAdapter()),
                BitField('blue', 0x00000000FFFF0000, adapter=U16ByteSwapAdapter()),
                BitField('clear', 0x000000000000FFFF, adapter=U16ByteSwapAdapter())
            ), bit_width=64, read_only=True),

            Register('DINT_DATA', 0x58, fields=(
                BitField('data', 0xFFFF, adapter=U16ByteSwapAdapter()),
            ), bit_width=16),

            Register('INTERRUPT', 0x60, fields=(
                BitField('status', 0b10000000, read_only=True),
                BitField('latch', 0b00010000, adapter=LookupAdapter({0: 1, 1: 0})),
                BitField('source', 0b00001100, read_only=True, adapter=LookupAdapter({
                    'red': 0b00,
                    'green': 0b01,
                    'blue': 0b10,
                    'clear': 0b11
                })),
                BitField('enable', 0b00000001)
            )),

            # 00: Interrupt status is toggled at each measurement end
            # 01: Interrupt status is updated at each measurement end
            # 10: Interrupt status is updated if 4 consecutive threshold judgements are the same
            # 11: Blah blah ditto above except for 8 consecutive judgements
            Register('PERSISTENCE', 0x61, fields=(
                BitField('mode', 0b00000011, adapter=LookupAdapter({
                    'toggle': 0b00,
                    'update': 0b01,
                    'update_on_4': 0b10,
                    'update_on_8': 0b11
                })),
            )),

            # High threshold defaults to 0xFFFF
            # Low threshold defaults to 0x0000
            Register('THRESHOLD', 0x62, fields=(
                BitField('high', 0xFFFF0000, adapter=U16ByteSwapAdapter()),
                BitField('low', 0x0000FFFF, adapter=U16ByteSwapAdapter())
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
                        name = 'BH1745_{register}_{field}_{key}'.format(
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
    def ready(self):
        """Return true if setup has been successful."""
        return self._is_setup

    def setup(self, i2c_addr=None, timeout=BH1745_RESET_TIMEOUT_SEC):
        """Set up the bh1745 sensor.

        :param i2c_addr: Optional i2c_addr to switch to

        """
        if self._is_setup:
            return True

        if timeout <= 0:
            raise ValueError('Device timeout period must be greater than 0')

        if i2c_addr is not None:
            self._bh1745.select_address(i2c_addr)

        try:
            self._bh1745.get('SYSTEM_CONTROL')
        except IOError:
            raise RuntimeError('BH1745 not found: IO error attempting to query device!')

        if self._bh1745.get('SYSTEM_CONTROL').part_id != 0b001011 or self._bh1745.get('MANUFACTURER').id != 0xE0:
            raise RuntimeError('BH1745 not found: Manufacturer or Part ID mismatch!')

        self._is_setup = True

        self._bh1745.set('SYSTEM_CONTROL', sw_reset=1)

        t_start = time.time()

        pending_reset = True

        while time.time() - t_start < timeout:
            if not self._bh1745.get('SYSTEM_CONTROL').sw_reset:
                pending_reset = False
                break
            time.sleep(0.01)

        if pending_reset:
            raise BH1745TimeoutError('Timeout waiting for BH1745 to reset.')

        self._bh1745.set('SYSTEM_CONTROL', int_reset=0)
        self._bh1745.set('MODE_CONTROL1', measurement_time_ms=320)
        self._bh1745.set('MODE_CONTROL2', adc_gain_x=1, rgbc_en=1)
        self._bh1745.set('MODE_CONTROL3', on=1)
        self._bh1745.set('THRESHOLD', low=0xFFFF, high=0x0000)
        self._bh1745.set('INTERRUPT', latch=1)

        time.sleep(0.320)

    def set_measurement_time_ms(self, time_ms):
        """Set the measurement time in milliseconds.

        :param time_ms: The time in milliseconds: 160, 320, 640, 1280, 2560, 5120

        """
        self.setup()
        self._bh1745.set('MODE_CONTROL1', measurement_time_ms=time_ms)

    def set_adc_gain_x(self, gain_x):
        """Set the ADC gain multiplier.

        :param gain_x: Must be either 1, 2 or 16

        """
        self.setup()
        self._bh1745.set('MODE_CONTROL2', adc_gain_x=gain_x)

    def set_leds(self, state):
        """Toggle the onboard LEDs.

        :param state: Either 1 for on, or 0 for off

        """
        self.setup()
        self._bh1745.set('INTERRUPT', enable=1 if state else 0)

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
        """Return the raw Red, Green, Blue and Clear readings."""
        self.setup()
        colour_data = self._bh1745.get('COLOUR_DATA')
        r, g, b, c = colour_data.red, colour_data.green, colour_data.blue, colour_data.clear

        if self._enable_channel_compensation:
            cr, cg, cb, cc = self._channel_compensation
            r, g, b, c = r * cr, g * cg, b * cb, c * cc

        return (r, g, b, c)

    def get_rgb_clamped(self):
        """Return an RGB value scaled against max(r, g, b).

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
        """Return an RGB value scaled against the clear channel."""
        r, g, b, c = self.get_rgbc_raw()

        if c > 0:
            r, g, b = [min(255, int((x / float(c)) * 255)) for x in (r, g, b)]
            return (r, g, b)

        return (0, 0, 0)
