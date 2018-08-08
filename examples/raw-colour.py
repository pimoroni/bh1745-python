import time
from h1745 import BH1745

bh1745 = BH1745()

bh1745.setup()
bh1745.set_leds(1)

while True:
    r, g, b, c = bh1745.get_rgbc_raw()
    print("RGBC: {:06d} {:06d} {:06d} {:06d}".format(r, g, b, c))
    time.sleep(1.0)
