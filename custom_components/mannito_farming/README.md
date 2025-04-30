# Mannito Farming Integration for Home Assistant

This custom integration allows you to control your Mannito Farming controller through Home Assistant.

## Features

- **5 Magnetic Valves** - Control water flow with on/off switches
- **10 Fans** - Control ventilation with on/off and speed control
- **8 Relays** - Control power outlets/sockets with on/off switches
- **4 Pumps** - Control liquid pumps with on/off switches
- **Automatic device discovery** via mDNS/zeroconf (if supported by your controller)
- **Periodic state updates** to keep Home Assistant in sync with your controller

## Requirements

- Home Assistant 2023.7.0 or newer
- Mannito Farming controller accessible on your local network
- Network connectivity between Home Assistant and the controller

## Installation

### HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Go to "Integrations"
3. Click the three dots in the top right corner and select "Custom repositories"
4. Add the URL to this repository and select "Integration" as the category
5. Click "Add"
6. Search for "Mannito Farming" and install it
7. Restart Home Assistant

### Manual Installation

1. Download this repository
2. Copy the `mannito_farming` folder to your Home Assistant's `custom_components` directory
3. Restart Home Assistant

## Configuration

### Automatic Discovery

If your controller supports mDNS/zeroconf advertising, Home Assistant should automatically discover it. You'll see a notification in the UI when a new Mannito Farming controller is discovered.

### Manual Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration" in the bottom right corner
3. Search for "Mannito Farming"
4. Enter the following information:
   - Host: The IP address or hostname of your controller
   - Username: (Optional) Authentication username
   - Password: (Optional) Authentication password

## Device Structure

Once configured, your controller will appear as a device in Home Assistant with the following entities:

- **Valve 1-5**: Switches for controlling the magnetic valves
- **Fan 1-10**: Fan entities with speed control
- **Relay 1-8**: Switches for controlling the power relays
- **Pump 1-4**: Switches for controlling the pumps

## API Endpoints

The integration uses the following API endpoints on your controller:

- Device state query: `http://{DEVICE_HOST}/api/device/{COMPONENT_NAME}/state` (GET)
- Device state control: `http://{DEVICE_HOST}/api/device/{COMPONENT_NAME}/state/{true/false}` (POST)
- Fan speed control: `http://{DEVICE_HOST}/api/device/{COMPONENT_NAME}/speed/{SPEED}` (POST)
- Device configuration: `http://{DEVICE_HOST}/api/device/config` (GET)

## Troubleshooting

### Controller Not Found

If your controller is not automatically discovered:
1. Make sure it's connected to the same network as your Home Assistant instance
2. Try adding it manually using its IP address
3. Check that your controller's firmware supports the required API endpoints

### Authentication Issues

If you're having authentication issues:
1. Double-check your username and password
2. Make sure your controller's firmware is up-to-date
3. Check your controller's documentation for any special authentication requirements

### Entities Not Updating

If your entities are not updating properly:
1. Check your network connection to the controller
2. Restart the integration by removing and re-adding it
3. Check your Home Assistant logs for any error messages

## Support

For issues and feature requests, please create an issue in the GitHub repository.