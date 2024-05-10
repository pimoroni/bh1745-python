# BH1745 Colour Sensor

[![Build Status](https://img.shields.io/github/actions/workflow/status/pimoroni/bh1745-python/test.yml?branch=main)](https://github.com/pimoroni/bh1745-python/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/pimoroni/bh1745-python/badge.svg?branch=main)](https://coveralls.io/github/pimoroni/bh1745-python?branch=main)
[![PyPi Package](https://img.shields.io/pypi/v/bh1745.svg)](https://pypi.python.org/pypi/bh1745)
[![Python Versions](https://img.shields.io/pypi/pyversions/bh1745.svg)](https://pypi.python.org/pypi/bh1745)

Most suited to detecting the illuminance and colour temperature of ambient light, the BH1745 senses Red, Green and Blue light and converts it to 16bit digital values.

## Installing

### Full install (recommended):

We've created an easy installation script that will install all pre-requisites and get your BH1745
up and running with minimal efforts. To run it, fire up Terminal which you'll find in Menu -> Accessories -> Terminal
on your Raspberry Pi desktop, as illustrated below:

![Finding the terminal](http://get.pimoroni.com/resources/github-repo-terminal.png)

In the new terminal window type the command exactly as it appears below (check for typos) and follow the on-screen instructions:

```bash
git clone https://github.com/pimoroni/bh1745-python
cd bh1745-python
./install.sh
```

**Note** Libraries will be installed in the "pimoroni" virtual environment, you will need to activate it to run examples:

```
source ~/.virtualenvs/pimoroni/bin/activate
```

### Development:

If you want to contribute, or like living on the edge of your seat by having the latest code, you can install the development version like so:

```bash
git clone https://github.com/pimoroni/bh1745-python
cd bh1745-python
./install.sh --unstable
```

The install script should do it for you, but in some cases you might have to enable the i2c bus.

On a Raspberry Pi you can do that like so:

```
sudo raspi-config nonint do_i2c 0
```
