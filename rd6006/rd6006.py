from pymodbus.client.sync import ModbusRtuFramer, ModbusTcpClient as ModbusClient
from sys import argv

class RD6006:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.instrument = ModbusClient(host=host, port=port, framer=ModbusRtuFramer)
        self.instrument.connect()
        regs = self._read_registers(0, 4)
        self.sn = regs[1] << 16 | regs[2]
        self.fw = regs[3] / 100
        self.type = int(regs[0] / 10)

        self.voltage_resolution = 100
        self.power_resolution = 100

        if self.type == 6012 or self.type == 6018:
            print("RD6012 or RD6018 detected")
            self.current_resolution = 100
        else:
            print("RD6006 or other detected")
            self.current_resolution = 1000

    def __repr__(self):
        return f"RD6006 SN:{self.sn} FW:{self.fw}"

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

    def _mem(self, M=0):
        """reads the 4 register of a Memory[0-9] and print on a single line"""
        regs = self._read_registers(M * 4 + 80, 4)
        print(
            f"M{M}: {regs[0] / self.voltage_resolution:4.1f}V, {regs[1] / self.current_resolution:3.3f}A, OVP:{regs[2] / self.voltage_resolution:4.1f}V, OCP:{regs[3] / self.current_resolution:3.3f}A"
        )

    def status(self):
        regs = self._read_registers(0, 84)
        print("== Device")
        print(f"Model   : {regs[0]/10}")
        print(f"SN      : {(regs[1]<<16 | regs[2]):08d}")
        print(f"Firmware: {regs[3]/100}")
        print(f"Input   : {regs[14] / self.voltage_resolution}V")
        if regs[4]:
            sign = -1
        else:
            sign = +1
        print(f"Temp    : {sign * regs[5]}°C")
        if regs[34]:
            sign = -1
        else:
            sign = +1
        print(f"TempProb: {sign * regs[35]}°C")
        print("== Output")
        print(f"Voltage : {regs[10] / self.voltage_resolution}V")
        print(f"Current : {regs[11] / self.current_resolution}A")
        print(f"Energy  : {regs[12]/1000}Ah")
        print(f"Power   : {regs[13]/100}W")
        print("== Settings")
        print(f"Voltage : {regs[8] / self.voltage_resolution}V")
        print(f"Current : {regs[9] / self.current_resolution}A")
        print("== Protection")
        print(f"Voltage : {regs[82] / self.voltage_resolution}V")
        print(f"Current : {regs[83] / self.current_resolution}A")
        print("== Battery")
        if regs[32]:
            print("Active")
            print(f"Voltage : {regs[33] / self.voltage_resolution}V")
        print(
            f"Capacity: {(regs[38] <<16 | regs[39])/1000}Ah"
        )  # TODO check 8 or 16 bits?
        print(
            f"Energy  : {(regs[40] <<16 | regs[41])/1000}Wh"
        )  # TODO check 8 or 16 bits?
        print("== Memories")
        for m in range(10):
            self._mem(M=m)

    @property
    def input_voltage(self):
        return self._read_register(14) / self.voltage_resolution

    def _read_temperature(self, base_register):
        regs = self._read_registers(base_register, 2)
        sign = 1
        if regs[0]:
            sign = -1
        return sign * regs[1]

    @property
    def temperature_internal(self):
        return self._read_temperature(4)

    @property
    def temperature_internal_fahrenheit(self):
        return self._read_temperature(6)

    @property
    def temperature_probe(self):
        return self._read_temperature(34)

    @property
    def temperature_probe_fahrenheit(self):
        return self._read_temperature(36)

    @property
    def target_voltage(self):
        return self._read_register(8) / self.voltage_resolution

    @target_voltage.setter
    def target_voltage(self, value):
        self._write_register(8, int(value * self.voltage_resolution))

    @property
    def measured_voltage(self):
        return self._read_register(10) / self.voltage_resolution

    @property
    def measured_current(self):
        return self._read_register(11) / self.current_resolution

    @property
    def measured_power(self):
        return self._read_register(13) / self.power_resolution

    @property
    def measured_ampere_hours(self):
        return (
            self._read_register(38) << 16 | self._read_register(39)
        ) / 1000  # TODO check 16 or 8 bit

    @property
    def measured_watt_hours(self):
        return (
            self._read_register(40) << 16 | self._read_register(41)
        ) / 1000  # TODO check 16 or 8 bit

    @property
    def battery_mode(self):
        return self._read_register(32)

    @property
    def measured_battery_voltage(self):
        return self._read_register(33)

    @property
    def target_current(self):
        return self._read_register(9) / self.current_resolution

    @target_current.setter
    def target_current(self, value):
        self._write_register(9, int(value * self.current_resolution))

    @property
    def voltage_protection(self):
        return self._read_register(82) / self.voltage_resolution

    @voltage_protection.setter
    def voltage_protection(self, value):
        self._write_register(82, int(value * self.voltage_resolution))

    @property
    def current_protection(self):
        return self._read_register(83) / self.current_resolution

    @current_protection.setter
    def current_protection(self, value):
        self._write_register(83, int(value * self.current_resolution))

    @property
    def enable(self):
        return self._read_register(18)

    @enable.setter
    def enable(self, value):
        self._write_register(18, int(value))

    @property
    def ocpovp(self):
        return self._read_register(16)

    @property
    def CVCC(self):
        return self._read_register(17)

    @property
    def backlight(self):
        return self._read_register(72)

    @backlight.setter
    def backlight(self, value):
        self._write_register(72, value)

    @property
    def date(self):
        """returns the date as tuple: (year, month, day)"""
        regs = self._read_registers(48, 3)
        year = regs[0]
        month = regs[1]
        day = regs[2]
        return (year, month, day)

    @date.setter
    def date(self, value):
        """Sets the date, needs tuple with (year, month, day) as argument"""
        year, month, day = value
        self._write_register(48, year)
        self._write_register(49, month)
        self._write_register(50, day)

    @property
    def time(self):
        """returns the time as tuple: (h, m, s)"""
        regs = self._read_registers(51, 3)
        h = regs[0]
        m = regs[1]
        s = regs[2]
        return (h, m, s)

    @time.setter
    def time(self, value):
        """sets the time, needs time with (h, m, s) as argument"""
        h, m, s = value
        self._write_register(51, h)
        self._write_register(52, m)
        self._write_register(53, s)

if __name__ == "__main__":
    r = RD6006(argv[1], int(argv[2], 10))
    r.status()
