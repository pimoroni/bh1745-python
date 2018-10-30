# bh1745

`setup()`

Set up the sensor with initial values and configuration. Should be called before using any other methods, but is called automatically for you.

`ready()`

Returns `True` if the sensor instance has successfully been `setup()` and False otherwise.

`get_rgbc_raw()`

Return the Red, Green, Blue and Clear values from the sensor, with compensation applied.

`get_rgb_clamped()`

Return an RGB value scaled against `max(r, g, b)`.

This will clamp/saturate one of the colour channels, providing a clearer idea of what primary colour an object is most likely to be.

However the resulting colour reaidng will not be accurate for other purposes.

IE: a value of `(255,0,128)` would produce a result of approximately `(1.0, 0.0, 0.5)` since `max(255,0,128) == 255`, `255/255 = 1`, `0/255 = 0` and `128/255 = 0.50196`.

`get_rgb_scaled()`

Return an RGB value scaled against the clear (unfiltered) channel.

`set_channel_compensation(r, g, b, c)`

Set compensation scale factors for each channel.

If you intend to measure a particular class of objects, say a set of matching wooden blocks with similar reflectivity and paint finish, you should calibrate the channel compensation until you see colour values that broadly represent the colour of the objects you're testing.

The default values were derived by testing a set of 5 Red, Green, Blue, Yellow and Orange wooden blocks.

These scale factors are applied in `get_rgbc_raw` right after the raw values are read from the sensor.

`enable_white_balance(enable)`

Enable scale compensation with the values set via `set_channel_compensation`.

`set_leds(state)`

Set the onboard LEDs to state, 1/True for on, 0/False for off.

`set_adc_gain_x(gain_x)`

Set the ADC gain multiplier, must be either 1, 2 or 16 (for 1x, 2x or 16x)

`set_measurement_time_ms(time_ms)`

Set the measurement time in milliseconds, must be either 160, 320, 640, 1280, 2560 or 5120. The longer the measurement time, the more saturated your colour readings will be.

