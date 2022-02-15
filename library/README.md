# BH1745 Colour Sensor

[![Build Status](https://shields.io/github/workflow/status/pimoroni/bh1745-python/Python%20Tests.svg)](https://github.com/pimoroni/bh1745-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/bh1745-python/badge.svg?branch=master)](https://coveralls.io/github/pimoroni/bh1745-python?branch=master)
[![PyPi Package](https://img.shields.io/pypi/v/bh1745.svg)](https://pypi.python.org/pypi/bh1745-python)
[![Python Versions](https://img.shields.io/pypi/pyversions/bh1745.svg)](https://pypi.python.org/pypi/bh1745-python)

Most suited to detecting the illuminance and colour temperature of ambient light, the BH1745 senses Red, Green and Blue light and converts it to 16bit digital values.

# Installing

Stable library from PyPi:

* Just run `python3 -m pip install bh1745`

Latest/development library from GitHub:

* `git clone https://github.com/pimoroni/bh1745-python`
* `cd bh1745-python`
* `sudo ./install.sh --unstable`


# Changelog
0.0.4
-----

* Migrate to new i2cdevice API

0.0.3
-----

* Automagically call setup if not called by user
* Allow setup() to try alternate i2c addresses
* Added .ready() to determine if sensor is setup

0.0.2
-----

* Bumped i2cdevice dependency to >=0.0.4

0.0.1
-----

* Initial Release
