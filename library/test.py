import time
from bh1745 import _bh1745 as l
import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.OUT)
#GPIO.output(4, GPIO.LOW)
try:
    l.SYSTEM_CONTROL.get_part_id()
except IOError:
    addr = l.bh1745.next_address()
    print("Trying alternate i2c address: 0x{:02x}".format(addr))
    l.SYSTEM_CONTROL.get_part_id()

assert l.SYSTEM_CONTROL.get_part_id() == 0b001011
assert l.MANUFACTURER.get_id() == 0xE0

print("""
Found BH1745
Part ID: 0x{:02x}
Manufacturer ID: 0x{:02x}
""".format(
    l.SYSTEM_CONTROL.get_part_id(),
    l.MANUFACTURER.get_id()
))

l.SYSTEM_CONTROL.set_sw_reset(1)

try:
    while True:
        reset = l.SYSTEM_CONTROL.get_sw_reset()
        if not reset:
            break
        time.sleep(1.0)
except KeyboardInterrupt:
    pass

l.SYSTEM_CONTROL.set_int_reset(0)

l.MODE_CONTROL1.set_measurement_time_ms(320)
l.MODE_CONTROL2.set_adc_gain_x(1)
l.MODE_CONTROL2.set_rgbc_en(1)
l.MODE_CONTROL3.set_on(1) # Writes 0x02 to 0x44
l.THRESHOLD.set_low(0xFFFF)
l.THRESHOLD.set_high(0x0000)

l.INTERRUPT.set_latch(1)
l.INTERRUPT.set_enable(1)

try:
    while True:
        with l.COLOUR_DATA as COLOUR_DATA:
            r, g, b, c = COLOUR_DATA.get_red(), COLOUR_DATA.get_green(), COLOUR_DATA.get_blue(), COLOUR_DATA.get_clear()

        print(r, g, b, c)

        div = max(r, g, b)

        if div > 0:
            r, g, b = [int((x / float(div)) * 255) for x in (r, g, b)]

        print("#{:02x}{:02x}{:02x}".format(r, g, b))

        time.sleep(0.5)
except KeyboardInterrupt:
    l.INTERRUPT.set_enable(0)
