import sys
import mock
import pytest


def test_setup_not_present():
    sys.modules['smbus'] = mock.MagicMock()
    from bh1745 import BH1745
    bh1745 = BH1745()
    with pytest.raises(RuntimeError):
        bh1745.setup()


def test_setup_mock_timeout():
    from tools import SMBusFakeDevice
    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules['smbus'] = smbus
    from bh1745 import BH1745, BH1745TimeoutError
    bh1745 = BH1745()
    with pytest.raises(BH1745TimeoutError):
        bh1745.setup(timeout=0.01)


def test_setup_mock_present():
    from tools import SMBusFakeDeviceNoTimeout
    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules['smbus'] = smbus
    from bh1745 import BH1745
    bh1745 = BH1745()
    bh1745.setup(timeout=0.01)
