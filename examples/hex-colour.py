import time
import bh1745

bh1745.setup()
bh1745.set_leds(1)

while True:
    r, g, b = bh1745.get_rgb_scaled()
    print("#{:02x}{:02x}{:02x}".format(r, g, b))
    time.sleep(1.0)
