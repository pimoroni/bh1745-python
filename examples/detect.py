#!/usr/bin/env python

import bh1745

colour = bh1745.BH1745()

for i2c_addr in bh1745.I2C_ADDRESSES:
    try:
        colour.setup(i2c_addr=i2c_addr)
        print("Found bh1745 on 0x{:02x}".format(i2c_addr))
        break
    except RuntimeError:
        pass

if not colour.ready():
    raise RuntimeError("No bh1745 found!")
