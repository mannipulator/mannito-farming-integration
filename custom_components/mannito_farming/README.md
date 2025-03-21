# Grow Controller Integration for Home Assistant

This custom integration allows you to control your ESP32-based grow controller through Home Assistant.

## Features

- Control 5 magnetic valves (as switches)
- Control 10 ventilators with speed control
- Control 4 dosing pumps (as switches)
- Control 1 dimmable light
- Control 8 power sockets
- Monitor 2 temperature/humidity sensors
- Automatic sensor state updates

## Installation

1. Download this repository
2. Copy the `grow_controller` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings -> Devices & Services
2. Click "Add Integration"
3. Search for "Grow Controller"
4. Enter the following information:
   - Host: The IP address of your ESP32 controller
   - Username: Your controller's username
   - Password: Your controller's password

## API Endpoints

The integration uses the following API endpoints:

- Device status: `http://<host>:80/api/device/<device_id>`
- Device control: `http://<host>:80/api/device/<device_id>/<command>`
- Sensor updates: `http://<host>:80/api/sensor`

## Device IDs

The integration uses the following device IDs:

- Valves: `valve_1` through `valve_5`
- Fans: `fan_1` through `fan_10`
- Pumps: `pump_1` through `pump_4`
- Light: `light_1`
- Sensors: `sensor_1` and `sensor_2`

## Requirements

- Home Assistant 2023.1 or newer
- ESP32 controller with the appropriate firmware
- Network connectivity between Home Assistant and the controller

## Support

For issues and feature requests, please create an issue in the GitHub repository. 