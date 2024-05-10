# noqa D100
import sys

import mock
import pytest


def test_setup_id_mismatch():
    """Test an attempt to set up the BH1745 with invalid sensor present."""
    sys.modules["smbus2"] = mock.MagicMock()
    from bh1745 import BH1745

    bh1745 = BH1745()
    with pytest.raises(RuntimeError):
        bh1745.setup()


def test_setup_not_present():
    """Test an attempt to set up the BH1745 with no sensor present."""
    from tools import SMBusFakeDeviceIOError

    from bh1745 import BH1745

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceIOError
    sys.modules["smbus2"] = smbus
    bh1745 = BH1745()
    with pytest.raises(RuntimeError):
        bh1745.setup()


def test_setup_mock_invalid_timeout():
    """Test an attempt to set up the BH1745 with a reset timeout."""
    from tools import SMBusFakeDevice

    from bh1745 import BH1745

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules["smbus2"] = smbus

    with pytest.raises(ValueError):
        bh1745 = BH1745()
        bh1745.setup(timeout=0)

    with pytest.raises(ValueError):
        bh1745 = BH1745()
        bh1745.setup(timeout=-1)


def test_setup_mock_timeout():
    """Test an attempt to set up the BH1745 with a reset timeout."""
    from tools import SMBusFakeDevice

    from bh1745 import BH1745, BH1745TimeoutError

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules["smbus2"] = smbus
    bh1745 = BH1745()
    with pytest.raises(BH1745TimeoutError):
        bh1745.setup(timeout=0.01)


def test_setup_mock_present():
    """Test an attempt to set up a present and working (mocked) BH1745."""
    from tools import SMBusFakeDeviceNoTimeout

    from bh1745 import BH1745

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules["smbus2"] = smbus
    bh1745 = BH1745()
    bh1745.setup(timeout=0.01)


def test_i2c_addr():
    """Test various valid and invalid i2c addresses for BH1745."""
    from tools import SMBusFakeDeviceNoTimeout

    from bh1745 import BH1745

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules["smbus2"] = smbus

    with pytest.raises(ValueError):
        bh1745 = BH1745(i2c_addr=0x40)

    with pytest.raises(ValueError):
        bh1745 = BH1745()
        bh1745.setup(i2c_addr=0x40)

    bh1745 = BH1745(i2c_addr=0x38)
    bh1745 = BH1745(i2c_addr=0x39)

    del bh1745


def test_is_setup():
    """Test ready() returns correct state."""
    from tools import SMBusFakeDeviceNoTimeout

    from bh1745 import BH1745

    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules["smbus2"] = smbus

    bh1745 = BH1745()
    assert bh1745.ready() is False

    bh1745.setup()
    assert bh1745.ready() is True
