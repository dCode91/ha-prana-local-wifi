# Prana Recuperator Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A Home Assistant custom integration for controlling Prana Recuperator ventilation devices via their local API.

## Features

- **Automatic Discovery**: Devices are automatically discovered via mDNS/Zeroconf
- **Fan Control**: Control supply, extract, and bounded (both) fans
- **Speed Control**: 6-speed control for all fans
- **Mode Switches**: Control various device modes:
  - Bound Mode (synchronized fans)
  - Heater
  - Winter Mode
  - Auto Mode
  - Auto+ Mode
  - Night Mode
  - Boost Mode
- **Sensors**: Read device sensors when available:
  - Inside/Outside Temperature
  - Humidity
  - CO2 levels
  - VOC levels
  - Air Pressure
  - Current fan speeds
- **Display Brightness**: Control the device display brightness (0-6 levels)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the repository URL and select "Integration" as the category
6. Click "Add"
7. Search for "Prana Recuperator" and install it
8. Restart Home Assistant

### Manual Installation

1. Download the `prana_recuperator` folder from this repository
2. Copy it to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Automatic Discovery

If your Prana device is on the same network, it should be automatically discovered. You'll see a notification in Home Assistant to set it up.

### Manual Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Prana Recuperator"
4. Enter the IP address of your device
5. Optionally, set a custom name
6. Click **Submit**

## Entities Created

### Numbers (Speed & Brightness Control)

| Entity | Description |
|--------|-------------|
| `number.prana_recuperator_supply_fan_speed` | Supply fan speed control (0-6) |
| `number.prana_recuperator_extract_fan_speed` | Extract fan speed control (0-6) |
| `number.prana_recuperator_recuperator_speed` | Bounded/Recuperator speed control (0-6) |
| `number.prana_recuperator_display_brightness` | Display brightness (0-6) |

### Switches

| Entity | Description |
|--------|-------------|
| `switch.prana_recuperator_bound_mode` | Synchronize supply and extract fans |
| `switch.prana_recuperator_heater` | Enable/disable the heater |
| `switch.prana_recuperator_winter_mode` | Winter operation mode |
| `switch.prana_recuperator_auto_mode` | Automatic operation |
| `switch.prana_recuperator_auto_plus_mode` | Enhanced automatic operation |
| `switch.prana_recuperator_night_mode` | Quiet night operation |
| `switch.prana_recuperator_boost_mode` | Maximum ventilation |

### Sensors (if available on your device)

| Entity | Description |
|--------|-------------|
| `sensor.prana_recuperator_inside_temperature` | Indoor temperature |
| `sensor.prana_recuperator_outside_temperature` | Outdoor temperature |
| `sensor.prana_recuperator_humidity` | Indoor humidity |
| `sensor.prana_recuperator_co2` | CO2 concentration |
| `sensor.prana_recuperator_voc` | VOC concentration |
| `sensor.prana_recuperator_air_pressure` | Air pressure |
| `sensor.prana_recuperator_extract_speed` | Current extract fan speed (1-6) |
| `sensor.prana_recuperator_supply_speed` | Current supply fan speed (1-6) |
| `sensor.prana_recuperator_bounded_speed` | Current bounded speed (1-6) |

## Example Automations

### Turn on ventilation when CO2 is high

```yaml
automation:
  - alias: "Ventilation - High CO2"
    trigger:
      - platform: numeric_state
        entity_id: sensor.prana_recuperator_co2
        above: 1000
    action:
      - service: number.set_value
        target:
          entity_id: number.prana_recuperator_recuperator_speed
        data:
          value: 4  # Speed 4 of 6
```

### Night mode schedule

```yaml
automation:
  - alias: "Ventilation - Night Mode On"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.prana_recuperator_night_mode

  - alias: "Ventilation - Night Mode Off"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.prana_recuperator_night_mode
```

### Winter mode based on outdoor temperature

```yaml
automation:
  - alias: "Ventilation - Winter Mode"
    trigger:
      - platform: numeric_state
        entity_id: sensor.prana_recuperator_outside_temperature
        below: 5
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.prana_recuperator_winter_mode
```

## Lovelace Card Example

```yaml
type: entities
title: Prana Recuperator
entities:
  - entity: number.prana_recuperator_recuperator_speed
    name: Ventilation Speed
  - entity: number.prana_recuperator_supply_fan_speed
    name: Supply Fan Speed
  - entity: number.prana_recuperator_extract_fan_speed
    name: Extract Fan Speed
  - type: divider
  - entity: switch.prana_recuperator_auto_mode
  - entity: switch.prana_recuperator_night_mode
  - entity: switch.prana_recuperator_winter_mode
  - entity: switch.prana_recuperator_boost_mode
  - type: divider
  - entity: sensor.prana_recuperator_inside_temperature
  - entity: sensor.prana_recuperator_outside_temperature
  - entity: sensor.prana_recuperator_humidity
  - entity: sensor.prana_recuperator_co2
  - type: divider
  - entity: number.prana_recuperator_display_brightness
```

## API Documentation

This integration uses the Prana Recuperator Local API. The device announces itself via mDNS with service type `_prana._tcp.local.` and communicates over HTTP on port 80.

### Endpoints Used

- `GET /getState` - Retrieves current device state
- `POST /setSpeed` - Sets fan speed
- `POST /setSpeedIsOn` - Turns fans on/off
- `POST /setSwitch` - Controls device modes
- `POST /setBrightness` - Sets display brightness

## Troubleshooting

### Device not discovered
1. Check the firmware version. Local API works only starting with Version 47.
2. Ensure your device is connected to the same network as Home Assistant
3. Check that mDNS/Bonjour is not blocked on your network
4. Try manual configuration using the device's IP address

### Cannot connect

1. Verify the device is powered on and connected to your network
2. Check the IP address is correct
3. Ensure port 80 is not blocked by a firewall
4. Try accessing `http://<device_ip>/getState` in a browser

### Entity shows unavailable

1. Check your network connectivity
2. The device may have changed IP address - try reconfiguring
3. Check the Home Assistant logs for error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by Prana. Use at your own risk.
