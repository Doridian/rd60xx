from pymodbus.client.sync import ModbusRtuFramer, ModbusTcpClient as ModbusClient
from sys import argv
from datetime import datetime

def _make_prop(register, read, write, factor=1):
    fget = None
    fset = None

    if isinstance(factor, str):
        if read:
            fget = lambda self: read(self, register) / getattr(self, factor)
        if write:
            fset = lambda self, val: write(self, register, val * getattr(self, factor))
    else:
        if read:
            fget = lambda self: read(self, register) / factor
        if write:
            fset = lambda self, val: write(self, register, val * factor)

    return property(fget, fset)

class RD60XX:
    PROTECTION_OK = 0
    PROTECTION_OVP = 1
    PROTECTION_OCP = 2

    OUTPUT_CV = 0
    OUTPUT_CC = 1

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.instrument = ModbusClient(host=host, port=port, framer=ModbusRtuFramer)
        self.instrument.connect()

        self.type = self._read_register(0) // 10
        self.sn = self._read_int32(1)
        self.fw = self._read_register(3) / 100

        self.voltage_resolution = 100
        self.power_resolution = 100

        if self.type == 6012 or self.type == 6018:
            self.current_resolution = 100
        else:
            self.current_resolution = 1000

    def __repr__(self):
        return f"RD{self.type} SN:{self.sn} FW:{self.fw}"

    def _read_register(self, register):
        return self._read_registers(register, 1)[0]

    def _read_registers(self, start, length):
        res = self.instrument.read_holding_registers(start, length, unit=1)
        if res.isError():
            raise res
        return res.registers

    def _write_register(self, register, value):
        res = self.instrument.write_register(register, value, unit=1)
        if res.isError():
            raise res

    def _write_registers(self, register, values):
        res = self.instrument.write_registers(address=register, values=values, unit=1)
        if res.isError():
            raise res

    def _read_signed_number(self, base_register):
        regs = self._read_registers(base_register, 2)
        sign = 1
        if regs[0]:
            sign = -1
        return sign * regs[1]

    def _read_int32(self, base_register):
        regs = self._read_registers(base_register, 2)
        return regs[0] << 16 | regs[1]

    input_volage = _make_prop(14, read=_read_register, write=None, factor="voltage_resolution")

    temperature_internal = _make_prop(4, read=_read_signed_number, write=None)
    temperature_internal_fahrenheit = _make_prop(6, read=_read_signed_number, write=None)
    temperature_probe = _make_prop(34, read=_read_signed_number, write=None)
    temperature_probe_fahrenheit = _make_prop(36, read=_read_signed_number, write=None)

    set_voltage = _make_prop(8, read=_read_register, write=_write_register, factor="voltage_resolution")
    set_current = _make_prop(9, read=_read_register, write=_write_register, factor="current_resolution")
    measured_voltage = _make_prop(10, read=_read_register, write=None, factor="voltage_resolution")
    measured_current = _make_prop(11, read=_read_register, write=None, factor="current_resolution")
    measured_power = _make_prop(13, read=_read_register, write=None, factor="power_resolution")

    protection_status = _make_prop(16, read=_read_register, write=None) # PROTECTION_*
    output_status = _make_prop(17, read=_read_register, write=None) # OUTPUT_CC / OUTPUT_CV
    output_enable = _make_prop(18, read=_read_register, write=_write_register)

    measured_capacity = _make_prop(38, read=_read_int32, write=None, factor=1000)
    measured_energy = _make_prop(40, read=_read_int32, write=None, factor=1000)

    protection_cutoff_voltage = _make_prop(82, read=_read_register, write=_write_register, factor="voltage_resolution")
    protection_cutoff_current = _make_prop(83, read=_read_register, write=_write_register, factor="current_resolution")

    battery_mode = _make_prop(32, read=_read_register, write=None)
    measured_battery_voltage = _make_prop(33, read=_read_register, write=None)

    backlight_brightness = _make_prop(72, read=_read_register, write=_write_register)

    @property
    def datetime(self):
        regs = self._read_registers(48, 6)
        return datetime(year=regs[0], month=regs[1], day=regs[2], hour=regs[3], minute=regs[4], second=regs[5])

    @datetime.setter
    def datetime(self, value):
        self._write_registers(48, [value.year, value.month, value.day, value.hour, value.minute, value.second])

    def sync_datetime(self):
        self.datetime = datetime.now()

if __name__ == "__main__":
    r = RD60XX(argv[1], int(argv[2], 10))
    print(r)
    r.sync_datetime()
    print(r.set_voltage)
