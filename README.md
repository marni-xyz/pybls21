# Blauberg S21 Modbus Python API

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

## Overview

**An asynchronous Python-based API for local control and monitoring of Blauberg S21 devices over Modbus/TCP.**

It is an **extended version** of **[jvitkauskas' development](https://github.com/jvitkauskas/pybls21)**. Many thanks for laying the foundation!

The major differences include:
- **Expanded attributes:** All temperatures, scheduler status
- **New control functions:** Timer mode and boost mode


## Usage

Initialization:

```python
client = S21Client("192.168.0.125", "502")
```

Polling:

```python
await client.poll()
```

Available methods to change B21 settings:
   Method                                      | Description                          |
 |---------------------------------------------|--------------------------------------|
 | `turn_on()` / `turn_off()`                  | Power on/off the device              |
 | `set_boost_on()` / `set_boost_off()`        | Enable/disable boost mode            |
 | `set_timer_on()` / `set_timer_off()`        | Enable/disable timer mode            |
 | `set_hvac_mode(hvac_mode: HVACMode)`        | Set HVAC mode                        |
 | `set_fan_mode(mode: int)`                   | Set fan mode                         |
 | `set_manual_fan_speed_percent(speed: int)`  | Set manual fan speed (0-100%)        |
 | `set_temperature(temp_celsius: int)`        | Set target temperature (°C)          |
 | `reset_filter_change_timer()`               | Reset timer for filter change        |
 | `reset_alarm()`                             | Reset all alarms                     |


## Testing

To check connectivity with and general output from your Blauberg S21 device, run:

```bash
python demo.py --host 192.168.0.125 --port 502
```

Run all tests:
```bash
python -m unittest -v
```

Run one test module:

```bash
python -m unittest -v tests.test_client
```

---

[buymecoffee]: https://www.buymeacoffee.com/marnixyz
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/marni-xyz/pybls21.svg?style=for-the-badge
[commits]: https://github.com/marni-xyz/pybls21/commits/main
[license-shield]: https://img.shields.io/github/license/marni-xyz/homeassistant_blauberg_s21.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40marni-xyz.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/marni-xyz/pybls21.svg?style=for-the-badge
[releases]: https://github.com/marni-xyz/pybls21/releases
[user_profile]: https://github.com/marni-xyz
