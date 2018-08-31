import struct
from i2cdevice import MockSMBus

BH1745_COLOUR_DATA = (666, 777, 888, 999)


class SMBusFakeDevice(MockSMBus):
    def __init__(self, i2c_bus):
        MockSMBus.__init__(self, i2c_bus)
        self.regs[0x40] = 0b001011     # Fake part number
        self.regs[0x92] = 0xE0         # Fake manufacturer ID

        colour_data = struct.pack("<HHHH", *BH1745_COLOUR_DATA)
        colour_data = [ord(x) if type(x) is str else x for x in colour_data]

        self.regs[0x50:0x50 + 8] = list(colour_data)


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
