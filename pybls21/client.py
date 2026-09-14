import asyncio
from typing import Any, Awaitable, Callable, List, Optional

# MaNi additions
import logging
_LOGGER = logging.getLogger(__name__)
# EO MaNi additions

from pymodbus.client import AsyncModbusTcpClient

from .constants import *
from .exceptions import (
    ModbusCommunicationException,
    UnsupportedDeviceException,
)
from .models import (
    TEMP_CELSIUS,
    BypassMode,
    BypassType,
    ClimateDevice,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)


def _parse_firmware_version(firmware_info: List[int]) -> str:
    if not isinstance(firmware_info, list) or len(firmware_info) < 3:
        return "unknown"
    
    try:
        major, minor = firmware_info[0].to_bytes(2, "big")
        day, month = firmware_info[1].to_bytes(2, "big")
        year: int = firmware_info[2]
        return f"{major}.{minor} ({year}-{month:02d}-{day:02d})"

    except (ValueError, OverflowError):
        return "unknown"

def _to_signed_16bit(value: int) -> int:
    return value - 0x10000 if value > 0x7FFF else value


# birdie1 additions
def _parse_min_hours_days_to_min(datetime_info: List[int]) -> int:
    hours, minutes = datetime_info[0].to_bytes(2, "big")
    days: int = datetime_info[1]
    total_minutes = days * 1440 + hours * 60 + minutes

    return total_minutes
# EO birdie1 additions


class S21Client:
    def __init__(self, host: str, port: int = 502):
        self.host = host
        self.port = port
        self.client = AsyncModbusTcpClient(host=self.host, port=self.port)
        self.device: Optional[ClimateDevice] = None
        self.lock = asyncio.Lock()

    # -----------------------------------------------------------
    # Functions to get device information
    async def poll(self) -> ClimateDevice:
        return await self._do_with_connection(self._poll)

    async def _poll(self) -> ClimateDevice:
        # MaNi additions
        _LOGGER.debug("Polling device at %s:%s", self.host, self.port)
        # EO MaNi additions
        
        if (await self._read_input_registers(IR_DeviceTYPE, count=1))[0] != 1:
            raise UnsupportedDeviceException("Unsupported device (IR_DeviceTYPE != 1)")

        coils = await self._read_coils(0, count=4)
        holding_registers = await self._read_holding_registers(0, count=76)
        input_registers = await self._read_input_registers(0, count=54)

        is_on: bool = coils[CL_POWER]
        is_boosting: bool = coils[CL_Boost_MODE]
        set_temperature: int = holding_registers[HR_SetTEMP]
        current_humidity: int = input_registers[IR_CurRH_Int]
        filter_state: int = input_registers[IR_StateFILTER]
        alarm_state: int = input_registers[IR_ALARM]

        # MaNi additions — get details for alarm (only if active alarm/warning state)
        alarm_codes: list[int] = []
        if alarm_state > 0:
            alarm_codes = await self._read_alarm_codes()
        # EO MaNi additions

        max_fan_level: int = holding_registers[HR_MaxSPEED_MODE]
        current_fan_level: int = holding_registers[HR_SPEED_MODE]  # 255 - manual
        temp_air_before_heating_x10: int = _to_signed_16bit(
            input_registers[IR_CurTEMP_SuAirIn]
        )
        temp_air_after_heating_x10: int = _to_signed_16bit(
            input_registers[IR_CurTEMP_SuAirOut]
        )
        supply_fan_rpm: int = input_registers[IR_SuRPM]
        extract_fan_rpm: int = input_registers[IR_ExRPM]
        firmware_info: List[int] = input_registers[
            IR_VerMAIN_FMW_start : IR_VerMAIN_FMW_end + 1
        ]
        operation_mode: int = holding_registers[HR_OPERATION_MODE]
        manual_fan_speed_percent: int = holding_registers[HR_ManualSPEED]

        # MaNi additions
        is_timer: bool = coils[CL_TIMER]
        main_timer_sec: int = input_registers[IR_CurTIMER_TIME] & 0xFF           # Low Byte is seconds
        main_timer_min: int = ( input_registers[IR_CurTIMER_TIME] >> 8 ) & 0xFF  # High Byte is minutes
        main_timer_hrs: int = input_registers[IR_CurTIMER_TIME_HRS] & 0xFF       # Low Byte (padding-safe)
        
        is_schedule: bool = coils[CL_WEEK]
        current_schedule_mode_speed: int = input_registers[IR_CurWeekSpeed]  # 0 - manual
        
        bypass_type: BypassType = BypassType(holding_registers[HR_BYPASS_ROTOR_TYPE])
        bypass_mode: BypassMode = BypassMode(holding_registers[HR_BYPASS_ROTOR_MODE])
        bypass_position_manual: int = holding_registers[HR_BYPASS_ROTOR_SET_MANUAL]
        bypass_position: int = input_registers[IR_BYPASS_ROTOR_STATUS]

        temp_air_extract_x10: int = _to_signed_16bit(
            input_registers[IR_CurTEMP_ExAirIn]
        )
        temp_air_exhaust_x10: int = _to_signed_16bit(
            input_registers[IR_CurTEMP_ExAirOut]
        )
        filter_countdown_days: int = input_registers[IR_CurFILTER_TIMER_DAYS]
        filter_countdown_hrs: int = ( input_registers[IR_CurFILTER_TIMER_HRS_MIN] >> 8 ) & 0xFF  # High Byte is hours
        filter_countdown_min: int = input_registers[IR_CurFILTER_TIMER_HRS_MIN] & 0xFF           # Low Byte (padding-safe) is minutes
        supply_pressure: int = input_registers[IR_CurSuPRESS]
        extract_pressure: int = input_registers[IR_CurExPRESS]
        # EO MaNi additions
        
        # birdie1 additions
        engine_running_time: List[int] = input_registers[
            IR_TotalWorkingTime_HRS_MIN : IR_TotalWorkingTime_DAYS + 1
        ]
        supply_airflow: int = input_registers[IR_CurSuAirFLOW]
        extract_airflow: int = input_registers[IR_CurExAirFLOW]
        supply_fan_speed: int = input_registers[IR_CurSuFanSPEED]
        extract_fan_speed: int = input_registers[IR_CurExFanSPEED]
        # EO birdie1 additions

        self.device = ClimateDevice(
            available=True,
            name="Blauberg S21",
            unique_id=f"S21_{self.host}_{self.port}",
            temperature_unit=TEMP_CELSIUS,  # Seems like no Fahrenheit option is available
            precision=1,
            current_temperature=temp_air_after_heating_x10 / 10,
            target_temperature=set_temperature,
            target_temperature_step=1,
            min_temp=15,
            max_temp=30,
            current_humidity=None if current_humidity == 0 else current_humidity,
            hvac_mode=
                HVACMode.OFF if not is_on
                else HVACMode.FAN_ONLY if operation_mode == 0
                else HVACMode.HEAT if operation_mode == 1
                else HVACMode.COOL if operation_mode == 2
                else HVACMode.AUTO,
            hvac_action=
                HVACAction.OFF if not is_on
                else HVACAction.FAN if operation_mode == 0
                else HVACAction.HEATING if operation_mode == 1
                else HVACAction.COOLING if operation_mode == 2
                else HVACAction.HEATING if temp_air_before_heating_x10 < temp_air_after_heating_x10
                else HVACAction.COOLING if temp_air_before_heating_x10 > temp_air_after_heating_x10
                else HVACAction.IDLE,
            hvac_modes=[
                HVACMode.OFF,
                HVACMode.HEAT,
                HVACMode.COOL,
                HVACMode.AUTO,
                HVACMode.FAN_ONLY,
            ],
            
            # MaNi additions - fan level based on scheduled (prioritised) or manual mode
            ##fan_mode=current_fan_level,  # original considers manual level only and ignores override in boost or scheduled mode
            fan_mode=
                max_fan_level if is_boosting
                else max_fan_level if is_timer
                else current_schedule_mode_speed if is_schedule 
                else current_fan_level,
            # EO MaNi additions
            fan_modes=[x + 1 for x in range(max_fan_level)] + [255],
            supported_features=ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE,
            manufacturer="Blauberg",
            model="S21",
            sw_version=_parse_firmware_version(firmware_info),
            is_boosting=is_boosting,
            current_intake_temperature=temp_air_before_heating_x10 / 10,
            manual_fan_speed_percent=manual_fan_speed_percent,
            max_fan_level=max_fan_level,
            filter_state=filter_state,
            alarm_state=alarm_state,
            supply_fan_rpm=supply_fan_rpm,
            extract_fan_rpm=extract_fan_rpm,

            # MaNi additions
            alarm_codes=alarm_codes,
            current_supply_temperature=temp_air_after_heating_x10 / 10,  # fresh air from ventilation unit into rooms
            current_extract_temperature=temp_air_extract_x10 / 10,       # used air from rooms into ventilation unit
            current_exhaust_temperature=temp_air_exhaust_x10 / 10,       # used air from ventilation unit to outside 
            filter_countdown_days=filter_countdown_days,  # whole days until filter replacement
            filter_countdown_hrs=filter_countdown_hrs,    # whole hours until filter replacement
            filter_countdown_min=filter_countdown_min,    # whole minutes until filter replacement
            is_timer=is_timer,
            timer_countdown = f"{main_timer_hrs:02d}:{main_timer_min:02d}:{main_timer_sec:02d}",
            is_schedule_mode=is_schedule,
            fan_level_schedule_mode=current_schedule_mode_speed,
            fan_level_manual_mode=current_fan_level,
            bypass_type=bypass_type,
            bypass_mode=bypass_mode,
            bypass_position=bypass_position,
            bypass_position_manual=bypass_position_manual,
            supply_pressure=supply_pressure,
            extract_pressure=extract_pressure,
            # EO MaNi additions

            # birdie1 additions
            engine_running_time=_parse_min_hours_days_to_min(engine_running_time),
            supply_airflow=supply_airflow,
            extract_airflow=extract_airflow,
            supply_fan_speed=supply_fan_speed,
            extract_fan_speed=extract_fan_speed,
            # EO birdie1 additions
        )
        
        # MaNi additions
        _LOGGER.debug("Poll successful: mode=%s, fan=%s, temp=%s, alarm=%s",
                  self.device.hvac_mode, self.device.fan_mode, self.device.current_temperature, self.device.alarm_state)
        # EO MaNi additions
        
        return self.device


    # -----------------------------------------------------------
    # Functions to change individual settings
    async def set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self._do_with_connection(lambda: self._set_hvac_mode(hvac_mode))

    async def _set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        if hvac_mode == HVACMode.OFF:
            await self._set_turn_off()
        elif hvac_mode == HVACMode.FAN_ONLY:
            await self._set_turn_on()
            await self._write_register(HR_OPERATION_MODE, 0)
        elif hvac_mode == HVACMode.HEAT:
            await self._set_turn_on()
            await self._write_register(HR_OPERATION_MODE, 1)
        elif hvac_mode == HVACMode.COOL:
            await self._set_turn_on()
            await self._write_register(HR_OPERATION_MODE, 2)
        else:
            await self._set_turn_on()
            await self._write_register(HR_OPERATION_MODE, 3)

    # MaNi additions - use dynamic comparison based on real max level of device (can be < 5)
    #async def set_fan_mode(self, mode: int) -> None:
    #    self._validate_fan_mode(mode)
    async def set_fan_mode(self, mode: int, max_fan_level: int) -> None:
        self._validate_fan_mode(mode, max_fan_level)
    # EO MaNi additions
        await self._do_with_connection(lambda: self._set_fan_mode(mode))

    async def _set_fan_mode(self, mode: int) -> None:
        await self._write_register(HR_SPEED_MODE, mode)
    
    @staticmethod
    # MaNi additions - use dynamic comparison based on real max level of device (can be < 5)
    #def _validate_fan_mode(mode: int) -> None:
    #    if not isinstance(mode, int) or mode not in (1, 2, 3, 4, 5, 255):
    def _validate_fan_mode(mode: int, max_fan_level: int) -> None:
        valid = set(range(1, max_fan_level+1)) | {255}
        if not isinstance(mode, int) or mode not in valid:
            raise ValueError(f"Fan mode must be one of: {valid}; got: {mode}")
    # EO MaNi additions

    async def set_manual_fan_speed_percent(self, speed_percent: int) -> None:
        self._validate_manual_fan_speed_percent(speed_percent)
        await self._do_with_connection(
            lambda: self._set_manual_fan_speed_percent(speed_percent)
        )

    async def _set_manual_fan_speed_percent(self, speed_percent: int) -> None:
        await self._write_register(HR_ManualSPEED, speed_percent)

    @staticmethod
    def _validate_manual_fan_speed_percent(speed_percent: int) -> None:
        if not isinstance(speed_percent, int) or not 0 <= speed_percent <= 100:
            raise ValueError(f"Manual fan speed percent must be between 0 and 100; got: {speed_percent}")

    async def set_temperature(self, temp_celsius: int) -> None:
        self._validate_temperature(temp_celsius)
        await self._do_with_connection(lambda: self._set_temperature(temp_celsius))

    async def _set_temperature(self, temp_celsius: int) -> None:
        await self._write_register(HR_SetTEMP, temp_celsius)

    @staticmethod
    def _validate_temperature(temp_celsius: int) -> None:
        if not isinstance(temp_celsius, int) or not 15 <= temp_celsius <= 30:
            raise ValueError(f"Temperature must be between 15 and 30 °C; got: {temp_celsius}")

    async def reset_filter_change_timer(self) -> None:
        await self._do_with_connection(self._reset_filter_change_timer)

    async def _reset_filter_change_timer(self) -> None:
        await self._write_coil(CL_RESET_FILTER_TIMER, True)

    async def reset_alarm(self) -> None:
        await self._do_with_connection(self._reset_alarm)

    async def _reset_alarm(self) -> None:
        await self._write_coil(CL_RESET_ALARM, True)

    async def turn_on(self) -> None:
        await self._do_with_connection(self._set_turn_on)

    async def _set_turn_on(self) -> None:
        await self._write_coil(CL_POWER, True)

    async def turn_off(self) -> None:
        await self._do_with_connection(self._set_turn_off)

    async def _set_turn_off(self) -> None:
        await self._write_coil(CL_POWER, False)

    async def set_boost_on(self) -> None:
        await self._do_with_connection(self._set_boost_on)

    async def _set_boost_on(self) -> None:
        await self._write_coil(CL_BoostSWITCH_CTRL, True)

    async def set_boost_off(self) -> None:
        await self._do_with_connection(self._set_boost_off)

    async def _set_boost_off(self) -> None:
        await self._write_coil(CL_BoostSWITCH_CTRL, False)

    async def set_timer_on(self) -> None:
        await self._do_with_connection(self._set_timer_on)

    async def _set_timer_on(self) -> None:
        await self._write_coil(CL_TIMER, True)
    
    async def set_timer_off(self) -> None:
        await self._do_with_connection(self._set_timer_off)

    async def _set_timer_off(self) -> None:
        await self._write_coil(CL_TIMER, False)

    async def set_scheduler_mode_on(self) -> None:
        await self._do_with_connection(self._set_scheduler_mode_on)

    async def _set_scheduler_mode_on(self) -> None:
        await self._write_coil(CL_WEEK, True)
    
    async def set_scheduler_mode_off(self) -> None:
        await self._do_with_connection(self._set_scheduler_mode_off)

    async def _set_scheduler_mode_off(self) -> None:
        await self._write_coil(CL_WEEK, False)

    async def set_bypass_mode(self, mode: BypassMode) -> None:
        self._validate_bypass_mode(mode)
        mode = BypassMode(mode)
        await self._do_with_connection(lambda: self._set_bypass_mode(mode))

    async def _set_bypass_mode(self, mode: int) -> None:
        await self._write_register(HR_BYPASS_ROTOR_MODE, mode)

    @staticmethod
    def _validate_bypass_mode(mode: BypassMode) -> None:
        if mode not in BypassMode:
            raise ValueError(f"Bypass mode must be 0 (closed/start), 1 (open/stop), or 2 (auto); got: {mode}")

    async def set_bypass_position(self, position_percent: int) -> None:
        self._validate_bypass_position(position_percent)
        await self._do_with_connection(
            lambda: self._set_bypass_position(position_percent)
        )

    async def _set_bypass_position(self, position_percent: int) -> None:
        await self._write_register(HR_BYPASS_ROTOR_SET_MANUAL, position_percent)
    
    @staticmethod
    def _validate_bypass_position(position_percent: int) -> None:
        if not isinstance(position_percent, int) or not 0 <= position_percent <= 100:
            raise ValueError("Bypass position percent must be between 0 and 100")

    async def _read_alarm_codes(self) -> list[int]:
        """Read active alarm codes from Discrete Inputs 19-71."""
        DI_ALARM_START = 19
        DI_ALARM_COUNT = 53  # codes 0-52
        bits = await self._read_discrete_inputs(DI_ALARM_START, DI_ALARM_COUNT)
        return [i for i, active in enumerate(bits) if active]

    # -----------------------------------------------------------
    # Functions to connect, get individual information or write changes
    async def _do_with_connection(self, func: Callable[[], Awaitable[Any]]) -> Any:
        async with self.lock:  # Device does not support multiple connections
            if not await self.client.connect():
                # MaNi additions
                _LOGGER.error("Failed to open Modbus TCP connection to %s:%s", self.host, self.port)
                # EO MaNi additions
                raise ModbusCommunicationException("Failed to open Modbus TCP connection")

            try:
                return await func()
            # MaNi additions
            #except Exception:
            except Exception as exc:
                _LOGGER.warning("Modbus operation failed for %s:%s: %s", self.host, self.port, exc)
                # EO MaNi additions
                if isinstance(self.device, ClimateDevice):
                    self.device.available = False
                raise
            finally:
                self.client.close()  # Also, long connections break over time and become unusable

    def _get_registers(self, response: Any, count: int, operation: str) -> List[int]:
        registers = getattr(self._validate_modbus_response(response, operation), "registers", None)
        if not isinstance(registers, list) or len(registers) < count:
            raise ModbusCommunicationException(
                f"Modbus {operation} failed: expected {count} registers"
            )
        return registers

    def _get_bits(self, response: Any, count: int, operation: str) -> List[bool]:
        bits = getattr(self._validate_modbus_response(response, operation), "bits", None)
        if not isinstance(bits, list) or len(bits) < count:
            raise ModbusCommunicationException(
                f"Modbus {operation} failed: expected {count} coil bits"
            )
        return bits

    async def _read_input_registers(self, address: int, count: int) -> List[int]:
        response = await self.client.read_input_registers(address, count=count)
        return self._get_registers(response, count, f"read input registers at {address}")

    async def _read_holding_registers(self, address: int, count: int) -> List[int]:
        response = await self.client.read_holding_registers(address, count=count)
        return self._get_registers(response, count, f"read holding registers at {address}")

    async def _read_coils(self, address: int, count: int) -> List[bool]:
        response = await self.client.read_coils(address, count=count)
        return self._get_bits(response, count, f"read coils at {address}")

    async def _read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        response = await self.client.read_discrete_inputs(address, count=count)
        return self._get_bits(response, count, f"read discrete inputs at {address}")

    async def _write_register(self, address: int, value: int) -> None:
        response = await self.client.write_register(address, value)
        self._validate_modbus_response(response, f"write register {address}")

    async def _write_coil(self, address: int, value: bool) -> None:
        response = await self.client.write_coil(address, value)
        self._validate_modbus_response(response, f"write coil {address}")

    @staticmethod
    def _validate_modbus_response(response: Any, operation: str) -> Any:
        if response is None:
            raise ModbusCommunicationException(f"Modbus {operation} failed: empty response")

        is_error = getattr(response, "isError", None)
        if callable(is_error) and response.isError():
            raise ModbusCommunicationException(
                f"Modbus {operation} failed: {response!r}"
            )

        return response
