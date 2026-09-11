"""Python library for Sentio Pro Sauna controllers - developed for Homeassistant."""

import logging
import re

import serialx
from serialx import SerialException

from .const import NAME, SERIAL_READ_TIMEOUT, VERSION

PYS_HVAC_MODE_OFF = "off"
PYS_HVAC_MODE_HEAT = "heat"
PYS_STATE_ON = "on"
PYS_STATE_OFF = "off"

__version__ = VERSION
_LOGGER = logging.getLogger(NAME)


class SentioPro:
    _sauna: bool = False
    _sauna_val = None
    _light: bool = False
    _light_val: int = 0
    _fan: bool = False
    _fan_val: int = 0
    _steam: bool | None = None
    _steam_val = None
    _i_switch: bool | None = None
    _i_switch_val: int | None = None
    _bench_temperature_val: int | None = None
    _heater_temperature_val: int | None = None
    _humidity_val: int | None = None
    _foil_temperature_val: int | None = None
    _timer: bool = False
    _timer_val: int = 1440
    _heattimer: bool = False
    _heattimer_val: int = 1440
    _user_prog: bool = False
    _user_prog_val: int = 1
    _config: str = ""
    _sw_version: str = ""
    _type: str = ""
    _status: str = ""

    def __init__(self, path, baud, timeout=SERIAL_READ_TIMEOUT):
        _LOGGER.debug("Starting pysentio - version: %s", VERSION)
        self._path = path
        self._baud = baud
        self._timeout = timeout
        self._serial = serialx.serial_for_url(
            self._path, self._baud, read_timeout=self._timeout
        )

    def open(self):
        self._serial.path = self._path
        self._serial.baudrate = self._baud
        self._serial.read_timeout = self._timeout
        self._serial.open()
        self._serial.reset_read_buffer()
        self._serial.reset_write_buffer()

    def close(self):
        self._serial.close()

    def _parse_response(self, resp):
        piece = resp.split(" ", maxsplit=2)
        pc1 = piece[1].lower().replace(";", "").strip()
        _LOGGER.debug("Parsed response->%s", piece[0])
        if piece[0] == "LIGHT":
            if pc1 == "on":
                self._light = True
            elif pc1 == "off":
                self._light = False
            else:
                self._light_val = int(pc1.replace("%", ""))

        elif piece[0] == "SAUNA":
            if pc1 == "on":
                self._sauna = True
            elif pc1 == "off":
                self._sauna = False
            else:
                self._sauna_val = int(pc1.replace("c", ""))

        elif piece[0] == "TEMP-BENCH":
            self._bench_temperature_val = int(pc1.replace("c", ""))

        elif piece[0] == "TEMP-HEATER":
            self._heater_temperature_val = int(pc1.replace("c", ""))

        elif piece[0] == "TEMP-FOIL":
            self._foil_temperature_val = int(pc1.replace("c", ""))

        elif piece[0] == "HUMIDITY":
            self._humidity_val = int(pc1.replace("%", ""))

        elif piece[0] == "FAN":
            if pc1 == "on":
                self._fan = True
            elif pc1 == "off":
                self._fan = False
            else:
                self._fan_val = int(pc1.replace("%", ""))

        elif piece[0] == "STEAM":
            if pc1 == "on":
                self._steam = True
            elif pc1 == "off":
                self._steam = False
            else:
                self._steam_val = int(pc1.replace("%", ""))

        elif piece[0] == "HEATTIMER":
            if pc1 == "on":
                self._heattimer = True
            elif pc1 == "off":
                self._heattimer = False
            else:
                self._heattimer_val = int(pc1.replace("min", ""))

        elif piece[0] == "TIMER":
            if pc1 == "on":
                self._timer = True
            elif pc1 == "off":
                self._timer = False
            else:
                self._timer_val = int(pc1.replace("min", ""))

        elif piece[0] == "CONFIG":
            piece2 = resp.replace(";", "")
            self._config = piece2

        elif piece[0] == "STATUS":
            piece2 = resp.replace(";", "")
            self._status = piece2.split()

        elif piece[0] == "INFO":
            piece2 = resp.replace(";", "")
            piece2 = piece2.split()
            self._sw_version = piece2[2]
            self._type = piece2[4]

    def update(self):
        self._write_read("get light\n")
        self._write_read("get light val\n")
        self._write_read("get sauna\n")
        self._write_read("get sauna val\n")
        self._write_read("get temp-bench val\n")
        self._write_read("get temp-heater val\n")
        self._write_read("get temp-foil val\n")
        self._write_read("get humidity val\n")
        self._write_read("get fan\n")
        self._write_read("get fan val\n")
        self._write_read("get timer\n")
        self._write_read("get timer val\n")
        self._write_read("get heattimer\n")
        self._write_read("get heattimer val\n")
        self._write_read("get i-switch\n")
        self._write_read("get i-switch val\n")
        self._write_read("get steam\n")
        self._write_read("get steam val\n")

    def get_config(self):
        self._write_read("get config\n")
        self._write_read("get info\n")

    def get_status(self):
        self._write_read("get status\n")

    def _write_cmd(self, cmd):
        """Write a cmd."""
        self._serial.write(cmd)

    def _write_read(self, msg):
        """Write to the port and read the return."""

        ret = ""

        try:
            if not self._serial.is_open:
                self._serial.open()
                _LOGGER.debug("Re-opening port")
            mesg = msg.encode("utf-8")
            _LOGGER.debug("Cmd->%s", msg)
            self._serial.write(mesg)
            ret = self._serial.read_until(b";\r\n", 400).decode("utf-8")
            _LOGGER.debug("Response->%s".strip(), ret)
            self._parse_response(ret)
        except (OSError, TimeoutError, SerialException):
            _LOGGER.error("Problem communicating with %s", self._path)
        #        self._serial.close()
        return ret

    @property
    def is_on(self) -> bool:
        return self._sauna

    def set_sauna(self, state) -> None:
        if state == PYS_STATE_ON:
            self._write_read("set sauna on\n")
        else:
            self._write_read("set sauna off\n")

    @property
    def sauna_val(self) -> int:
        return self._sauna_val

    @property
    def target_temperature(self) -> int:
        return self._sauna_val

    def set_sauna_val(self, val) -> int:
        self._write_read(f"set sauna val {val}\n")

    @property
    def light_is_on(self) -> bool:
        return self._light

    @property
    def light_val(self) -> int:
        return self._light_val

    def set_light(self, state: str) -> None:
        if state == PYS_STATE_ON:
            self._write_read("set light on\n")
        else:
            self._write_read("set light off\n")

    def set_light_val(self, val: int) -> None:
        self._write_read(f"set light val {val}\n")

    @property
    def fan(self) -> bool:
        return self._fan

    @property
    def fan_val(self) -> int:
        return self._fan_val

    def set_fan(self, state: str) -> None:
        if state == PYS_STATE_ON:
            self._write_read("set fan on\n")
        else:
            self._write_read("set fan off\n")

    def set_fan_val(self, val: int) -> None:
        self._write_read(f"set fan val {val}\n")

    @property
    def steam(self):
        return self._steam

    @property
    def steam_val(self):
        return self._steam_val

    def set_steam(self, state):
        if state == PYS_STATE_ON:
            self._write_read("set steam on\n")
        else:
            self._write_read("set steam off\n")

    def set_steam_val(self, val):
        self._write_read(f"set steam val {val}\n")

    @property
    def i_switch(self) -> bool | None:
        return self._i_switch

    @property
    def i_switch_val(self):
        return self._i_switch_val

    def set_i_switch(self, state):
        if state == PYS_STATE_ON:
            self._write_read("set i-switch on\n")
        else:
            self._write_read("set i-switch off\n")

    def set_i_switch_val(self, val):
        self._write_read(f"set i-switch val {val}\n")

    @property
    def heattimer_is_on(self) -> bool:
        return self._heattimer

    def set_heattimer(self, state):
        if state == PYS_STATE_ON:
            self._write_read("set heat-timer on\n")
        else:
            self._write_read("set heat-timer off\n")

    @property
    def heattimer_val(self) -> int:
        return self._heattimer_val

    def set_heattimer_val(self, val: int) -> None:
        self._write_read(f"set heat-timer val {val}\n")

    @property
    def timer_is_on(self) -> bool:
        return self._timer

    def set_timer(self, state: str) -> None:
        if state == PYS_STATE_ON:
            self._write_read("set timer on\n")
        else:
            self._write_read("set timer off\n")

    @property
    def timer_val(self) -> int:
        return self._timer_val

    def set_timer_val(self, val: int) -> None:
        self._write_read(f"set timer val {val}\n")

    @property
    def bench_temperature(self) -> int | None:
        return self._bench_temperature_val

    @property
    def heater_temperature(self) -> int | None:
        return self._heater_temperature_val

    @property
    def foil_temperature(self) -> int | None:
        return self._foil_temperature_val

    @property
    def humidity(self) -> int | None:
        return self._humidity_val

    @property
    def user_prog_is_on(self) -> bool:
        return self._user_prog

    @property
    def user_prog_val(self) -> int:
        return self._user_prog_val

    @property
    def hvac_mode(self) -> str:
        if self._sauna:
            return PYS_HVAC_MODE_HEAT
        else:
            return PYS_HVAC_MODE_OFF

    @property
    def sw_version(self) -> str:
        return self._sw_version

    @property
    def type(self) -> str:
        return self._type

    def config(self, opt: str) -> str | None:
        for line in self._config.lower().splitlines():
            if re.match(opt, line.lower()):
                st = re.split(opt, line)
                return st[1].strip()
        return None

    @property
    def config_raw(self) -> str:
        return self._config

    @property
    def status(self) -> str:
        return self._status
