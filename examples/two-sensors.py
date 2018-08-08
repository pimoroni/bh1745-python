import time
from bh1745 import BH1745

bh1745_a = BH1745(0x38) # Stock BH1745 breakout or jumper soldered
bh1745_b = BH1745(0x39) # Cuttable trace cut

bh1745_a.setup()
bh1745_b.setup()

bh1745_a.set_leds(1)
bh1745_b.set_leds(1)

try:
    while True:
        r, g, b = bh1745_a.get_rgb_scaled()
        print("A: #{:02x}{:02x}{:02x}".format(r, g, b))
        r, g, b = bh1745_b.get_rgb_scaled()
        print("B: #{:02x}{:02x}{:02x}".format(r, g, b))
        time.sleep(1.0)

except KeyboardInterrupt:
    bh1745_a.set_leds(0)
    bh1745_b.set_leds(0)