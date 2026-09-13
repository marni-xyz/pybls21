from enum import Enum
# MaNi - conversion to dataclass (more robust and mutable)
#from typing import List, NamedTuple, Optional
from dataclasses import dataclass, field
from typing import List, Optional
# EO MaNi - conversion to dataclass

TEMP_CELSIUS: str = "°C"


class ClimateEntityFeature(int, Enum):
    TARGET_TEMPERATURE = 1
    FAN_MODE = 8


class HVACMode(str, Enum):
    OFF =       "off"
    HEAT =      "heat"
    COOL =      "cool"
    AUTO =      "auto"
    FAN_ONLY =  "fan_only"


class HVACAction(str, Enum):
    COOLING =   "cooling"
    FAN =       "fan"
    HEATING =   "heating"
    IDLE =      "idle"
    OFF =       "off"


# MaNi - conversion to dataclass
#class ClimateDevice(NamedTuple):
@dataclass
class ClimateDevice:
# EO MaNi - conversion to dataclass
    available:                  bool
    name:                       str
    unique_id:                  str
    temperature_unit:           str
    precision:                  float
    current_temperature:        float
    target_temperature:         float
    target_temperature_step:    float
    max_temp:                   float
    min_temp:                   float
    hvac_mode:                  str
    hvac_action:                str
    hvac_modes:                 List[str]
    supported_features:         int
    manufacturer:               str
    is_boosting:                bool
    current_intake_temperature: float
    manual_fan_speed_percent:   int
    max_fan_level:              int
    filter_state:               int
    alarm_state:                int
    supply_fan_speed:           int
    extract_fan_speed:          int

    # MaNi additions
    current_ingoing_temperature: float
    current_extract_temperature: float
    current_exhaust_temperature: float
    is_timer:                    bool
    is_schedule_mode:            bool
    alarm_codes:                 list[int] = field(default_factory=list)
    # EO MaNi additions

    current_humidity: Optional[float] = None
    fan_mode:         Optional[int] = None
    fan_modes:        Optional[List[int]] = None
    model:            Optional[str] = None
    sw_version:       Optional[str] = None

    # MaNi additions
    filter_countdown_days:   Optional[int] = None
    filter_countdown_hrs:    Optional[int] = None
    filter_countdown_min:    Optional[int] = None
    timer_countdown:         Optional[str] = None
    supply_pressure:         Optional[int] = None
    extract_pressure:        Optional[int] = None
    fan_level_schedule_mode: Optional[int] = None
    fan_level_manual_mode:   Optional[int] = None
    bypass_type:             Optional[int] = None
    bypass_mode:             Optional[int] = None
    # EO MaNi additions
