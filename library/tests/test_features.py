# noqa D100
import sys
import mock


def _setup():
    global bh1745
    from tools import SMBusFakeDeviceNoTimeout
    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules['smbus'] = smbus
    from bh1745 import BH1745
    bh1745 = BH1745()


def test_get_rgbc_raw():
    """Test retriving raw RGBC data against mocked values."""
    from tools import BH1745_COLOUR_DATA
    _setup()
    bh1745.setup(timeout=0.01)

    # White balance will change the BH1745_COLOUR_DATA
    # and make our test fail. Disable it in this case.
    bh1745.enable_white_balance(False)

    colour_data = bh1745.get_rgbc_raw()

    assert colour_data == BH1745_COLOUR_DATA


def test_set_measurement_time_ms():
    """Test setting measurement time to valid and snapped value."""
    _setup()

    bh1745.set_measurement_time_ms(320)
    assert bh1745._bh1745.MODE_CONTROL1.get_measurement_time_ms() == 320

    # Should snap to 160
    bh1745.set_measurement_time_ms(100)
    assert bh1745._bh1745.MODE_CONTROL1.get_measurement_time_ms() == 160
