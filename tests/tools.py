"""Test tools for the BH1745 colour sensor."""
import struct

from i2cdevice import MockSMBus

BH1745_COLOUR_DATA = (666, 777, 888, 999)


class SMBusFakeDeviceIOError(MockSMBus):
    """Mock a BH1745 that returns an IOError in all cases."""

    def write_i2c_block_data(self, i2c_address, register, values):
        """Raise an IO Error for any write attempt."""
        raise IOError("IOError: Fake Device Not Found")

    def read_i2c_block_data(self, i2c_address, register, length):
        """Raise an IO Error for any read attempt."""
        raise IOError("IOError: Fake Device Not Found")


class SMBusFakeDevice(MockSMBus):
    """Mock a BH1745 with fake register data."""

    def __init__(self, i2c_bus):
        """Initialise device mock.

        :param i2c_bus: i2c bus ID

        """
        MockSMBus.__init__(self, i2c_bus)
        self.regs[0x40] = 0b001011     # Fake part number
        self.regs[0x92] = 0xE0         # Fake manufacturer ID

        colour_data = struct.pack("<HHHH", *BH1745_COLOUR_DATA)
        colour_data = [ord(x) if isinstance(x, str) else x for x in colour_data]

        self.regs[0x50 : 0x50 + 8] = list(colour_data)


class SMBusFakeDeviceNoTimeout(SMBusFakeDevice):
    """Mock a BH1745 with fake register data and successful reset.

    Overrides a read to register 0x40 to fake
    the reset bit being reset back to 0 by a
    successful device reset

    """

    def __init__(self, i2c_bus):
        """Initialise device mock.

        :param i2c_bus: i2c bus ID

        """
        SMBusFakeDevice.__init__(self, i2c_bus)

    def read_i2c_block_data(self, i2c_address, register, length):
        """Read up to length bytes from i2c device."""
        if register == 0x40:
            values = self.regs[register : register + length]
            values[0] &= 0b01111111  # Mask out the reset status bit
            return values
        return SMBusFakeDevice.read_i2c_block_data(self, i2c_address, register, length)
