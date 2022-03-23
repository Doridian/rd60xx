# RIDEN RD60XX Python module

This module allows to control a RD60XX via the network using Python (needs a flashed WiFi module with ESP-link or similar).

As with previous models, the RD60XX uses the Modbus protocol over serial, the
registers however are different than the DPS models. The registers are described
in the [registers.md](registers.md) file.

## Features

It allows to control the following options :
 * Output voltage and current
 * Protection voltage and current
 * Backlight
 * Enable status

## Installation
```
$ python setup.py install --user
```

## Usage

```
In [1]: from rd60xx import RD60XX
In [2]: r = RD60XX(ip=10.1.2.3, port=23)
In [3]: r.voltage=1.8
In [4]: r.enable=True
```
