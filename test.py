import time
import bh1745 as l
import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.OUT)
#GPIO.output(4, GPIO.LOW)

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
        #l.INTERRUPT.read()
        #status = l.INTERRUPT.get_status(False)
        #print("Status: {}".format(status))
        l.COLOUR_DATA.read()
        r, g, b, c = l.COLOUR_DATA.get_red(False), l.COLOUR_DATA.get_green(False), l.COLOUR_DATA.get_blue(False), l.COLOUR_DATA.get_clear(False)

        #print(r, g, b, c)
        div = max(r, g, b)

        if div > 0:
            r, g, b = [int((x / float(div)) * 255) for x in (r, g, b)]

        print("#{:02x}{:02x}{:02x}".format(r, g, b))

        time.sleep(0.5)
except KeyboardInterrupt:
    pass
