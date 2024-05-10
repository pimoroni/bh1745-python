#!/usr/bin/env python
import time

from bh1745 import BH1745

bh1745 = BH1745()

bh1745.setup()
bh1745.set_leds(1)

time.sleep(1.0)  # Skip the reading that happened before the LEDs were enabled

try:
    while True:
        r, g, b, c = bh1745.get_rgbc_raw()
        print(f"RGBC: {r:10.1f} {g:10.1f} {b:10.1f} {c:10.1f}")
        time.sleep(0.5)

except KeyboardInterrupt:
    bh1745.set_leds(0)
