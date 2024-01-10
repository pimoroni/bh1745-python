#!/usr/bin/env python
import bh1745

colour = bh1745.BH1745()

for i2c_addr in bh1745.I2C_ADDRESSES:
    try:
        colour.setup(i2c_addr=i2c_addr)
        print(f"Found bh1745 on 0x{i2c_addr:02x}")
        break
    except RuntimeError:
        pass

if not colour.ready():
    raise RuntimeError("No bh1745 found!")
