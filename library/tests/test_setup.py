import sys
import mock
import pytest
from i2cdevice import MockSMBus


class SMBusFakeDevice(MockSMBus):
    def __init__(self, i2c_bus):
        MockSMBus.__init__(self, i2c_bus)
        self.regs[0x40] = 0b001011     # Fake part number
        self.regs[0x92] = 0xE0         # Fake manufacturer ID


class SMBusFakeDeviceNoTimeout(SMBusFakeDevice):
    """Overrides a read to register 0x40 to fake
    the reset bit being reset back to 0 by a
    successful device reset"""
    def __init__(self, i2c_bus):
        SMBusFakeDevice.__init__(self, i2c_bus)

    def read_i2c_block_data(self, i2c_address, register, length):
        if register == 0x40:
            values = self.regs[register:register + length]
            values[0] &= 0b01111111  # Mask out the reset status bit
            return values
        return SMBusFakeDevice.read_i2c_block_data(self, i2c_address, register, length)


def test_setup_not_present():
    sys.modules['smbus'] = mock.MagicMock()
    from bh1745 import BH1745
    bh1745 = BH1745()
    with pytest.raises(RuntimeError):
        bh1745.setup()


def test_setup_mock_timeout():
    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDevice
    sys.modules['smbus'] = smbus
    from bh1745 import BH1745, BH1745TimeoutError
    bh1745 = BH1745()
    with pytest.raises(BH1745TimeoutError):
        bh1745.setup(timeout=0.01)


def test_setup_mock_present():
    smbus = mock.Mock()
    smbus.SMBus = SMBusFakeDeviceNoTimeout
    sys.modules['smbus'] = smbus
    from bh1745 import BH1745
    bh1745 = BH1745()
    bh1745.setup(timeout=0.01)
