# noqa D100
import sys

import mock


def _setup():
    global bh1745
    from tools import SMBusFakeDeviceNoTimeout

    from bh1745 import BH1745

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules["smbus2"] = smbus
    bh1745 = BH1745()


def test_set_adc_gain_x():
    """Test setting adc gain amount."""
    _setup()
    bh1745.setup(timeout=0.01)

    bh1745.set_adc_gain_x(1)
    assert bh1745._bh1745.MODE_CONTROL2.get_adc_gain_x() == 1

    # Should snap to 16x
    bh1745.set_adc_gain_x(15)
    assert bh1745._bh1745.MODE_CONTROL2.get_adc_gain_x() == 16


def test_get_rgbc_raw():
    """Test retrieving raw RGBC data against mocked values."""
    from tools import BH1745_COLOUR_DATA

    _setup()
    bh1745.setup(timeout=0.01)

    # White balance will change the BH1745_COLOUR_DATA
    # and make our test fail. Disable it in this case.
    bh1745.enable_white_balance(False)

    colour_data = bh1745.get_rgbc_raw()

    assert colour_data == BH1745_COLOUR_DATA


def test_get_rgbc_clamped():
    """Test retrieving raw RGBC data against mocked values."""
    from tools import BH1745_COLOUR_DATA

    _setup()
    bh1745.setup(timeout=0.01)

    # White balance will change the BH1745_COLOUR_DATA
    # and make our test fail. Disable it in this case.
    bh1745.enable_white_balance(False)

    colour_data = bh1745.get_rgb_clamped()

    r, g, b, c = BH1745_COLOUR_DATA

    scale = max(r, g, b)

    scaled_data = [int((x / float(scale)) * 255) for x in BH1745_COLOUR_DATA[0:3]]

    assert list(colour_data) == scaled_data


def test_get_rgbc_scaled():
    """Test retrieving raw RGBC data against mocked values."""
    from tools import BH1745_COLOUR_DATA

    _setup()
    bh1745.setup(timeout=0.01)

    # White balance will change the BH1745_COLOUR_DATA
    # and make our test fail. Disable it in this case.
    bh1745.enable_white_balance(False)

    colour_data = bh1745.get_rgb_scaled()

    scaled_data = [int((x / float(BH1745_COLOUR_DATA[3])) * 255) for x in BH1745_COLOUR_DATA[0:3]]

    assert list(colour_data) == scaled_data


def test_set_measurement_time_ms():
    """Test setting measurement time to valid and snapped value."""
    _setup()

    bh1745.set_measurement_time_ms(320)
    assert bh1745._bh1745.MODE_CONTROL1.get_measurement_time_ms() == 320

    # Should snap to 160
    bh1745.set_measurement_time_ms(100)
    assert bh1745._bh1745.MODE_CONTROL1.get_measurement_time_ms() == 160
