# Blauberg S21 Asynchronous Python API

An API allowing to get information and control settings of a Blauberg S21 device locally over Modbus/TCP.
It is an extended version of [jvitkauskas' development](https://github.com/jvitkauskas/pybls21). Without their efforts, this would not have been possible.

The major differences include:
- More attributes (all temperatures, scheduler status)
- Additional functions to change settings (timer and boost mode)

## Usage
To initialize:

`client = S21Client("192.168.0.125", "502")`


To load:

`await client.poll()`


The following functions to change B21 settings are available:
- `turn_on()`
- `turn_off()`
- `set_boost_on()`
- `set_boost_off()`
- `set_timer_on()`
- `set_timer_off()`
- `set_hvac_mode(hvac_mode: HVACMode)`
- `set_fan_mode(mode: int)`
- `set_manual_fan_speed_percent(speed_percent: int)`
- `set_temperature(temp_celsius: int)`
- `reset_filter_change_timer()`
- `reset_alarm()`


## Testing

To check connectivity and general output from your Blauberg S21 device:

`demo.py --host 192.168.0.125 --port 502`
