# Mannito Farming Integration for Home Assistant

[![License](https://img.shields.io/github/license/mannito-farming-solutions/mannito-farming-integration)](LICENSE)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.7.0%2B-blue.svg)](https://github.com/home-assistant/core)

This custom integration enables seamless control and monitoring of Mannito Farming controllers through Home Assistant. Transform your smart farming setup into a fully integrated home automation system with comprehensive device management and real-time monitoring capabilities.

## Overview

The Mannito Farming Integration bridges the gap between your agricultural automation systems and Home Assistant, providing unified control over irrigation, ventilation, lighting, and environmental monitoring. Whether you're managing a greenhouse, hydroponic system, or indoor growing operation, this integration offers professional-grade automation with the familiar Home Assistant interface.

## ✨ Features

### 🔧 Device Control
- **5 Magnetic Valves** - Precise irrigation control with on/off switching
- **10 Variable Speed Fans** - Complete ventilation management with speed control (1-100%)
- **8 Power Relays** - Control pumps, lights, heaters, and other electrical devices
- **4 Dosing Pumps** - Automated nutrient and water delivery systems

### 📊 Environmental Monitoring
- **Temperature Sensors** - Monitor ambient and root zone temperatures
- **Humidity Sensors** - Track relative humidity levels
- **CO2 Monitoring** - Carbon dioxide level measurement
- **pH Sensors** - Water and nutrient solution pH monitoring
- **Electrical Conductivity** - Nutrient concentration measurement
- **Water Flow Meters** - Monitor irrigation flow rates
- **Water Level Sensors** - Track reservoir and tank levels

### 🚀 Advanced Features
- **Automatic Device Discovery** - Zero-configuration setup via mDNS/Zeroconf
- **Real-time Updates** - Continuous synchronization with your controller
- **Local Network Operation** - Secure, low-latency communication
- **Cloud Support** *(Coming Soon)* - Remote access and monitoring capabilities
- **Home Assistant Integration** - Full compatibility with automations, scenes, and dashboards

## 📋 Requirements

- **Home Assistant 2023.7.0 or newer**
- **Mannito Farming Controller** with network connectivity
- **Local Network Access** between Home Assistant and the controller
- **Compatible Firmware** supporting the required API endpoints

## 🚀 Installation

### Method 1: HACS (Recommended)

[HACS](https://hacs.xyz/) provides the easiest installation and update experience:

1. **Install HACS** if you haven't already ([HACS Installation Guide](https://hacs.xyz/docs/setup/download))
2. **Open HACS** in your Home Assistant instance
3. **Navigate to Integrations**
4. **Click the three dots** (⋮) in the top right corner
5. **Select "Custom repositories"**
6. **Add this repository:**
   - **URL:** `https://github.com/mannito-farming-solutions/mannito-farming-integration`
   - **Category:** Integration
7. **Click "Add"**
8. **Search for "Mannito Farming"** and click "Install"
9. **Restart Home Assistant**

### Method 2: Manual Installation

For advanced users or custom setups:

1. **Download the latest release** from the [releases page](https://github.com/mannito-farming-solutions/mannito-farming-integration/releases)
2. **Extract the files** and copy the `mannito_farming` folder to your Home Assistant `custom_components` directory:
   ```
   /config/custom_components/mannito_farming/
   ```
3. **Restart Home Assistant**
4. **Verify installation** by checking the logs for any errors

## ⚙️ Configuration

### Automatic Discovery (Recommended)

If your Mannito Farming controller supports mDNS/Zeroconf advertising, Home Assistant will automatically discover it:

1. **Check for notifications** in the Home Assistant UI
2. **Click "Configure"** when the Mannito Farming device appears
3. **Enter credentials** if required (username/password)
4. **Complete setup** and start using your devices

### Manual Configuration

For controllers without automatic discovery or network-specific setups:

1. **Navigate to Settings** → **Devices & Services**
2. **Click "Add Integration"** (+ button in bottom right)
3. **Search for "Mannito Farming"**
4. **Enter connection details:**
   - **Host:** IP address or hostname of your controller (e.g., `192.168.1.100`)
   - **Username:** Authentication username *(optional)*
   - **Password:** Authentication password *(optional)*
5. **Click "Submit"** to complete configuration

## 🏠 Device Structure

Once configured, your Mannito Farming controller appears as a single device in Home Assistant with multiple entities:

### Irrigation System
- **Valve 1-5:** `switch.mannito_valve_1` through `switch.mannito_valve_5`
  - Control irrigation zones and water distribution
  - Simple on/off operation with status feedback

### Ventilation System  
- **Fan 1-10:** `fan.mannito_fan_1` through `fan.mannito_fan_10`
  - Variable speed control (1-100%)
  - Individual on/off control
  - Real-time speed monitoring

### Power Management
- **Relay 1-8:** `switch.mannito_relay_1` through `switch.mannito_relay_8`
  - Control high-power devices (pumps, heaters, lights)
  - Safety interlocks and status monitoring

### Fluid Management
- **Pump 1-4:** `switch.mannito_pump_1` through `switch.mannito_pump_4`
  - Dosing and circulation pump control
  - Flow monitoring and safety features

### Environmental Sensors
- **Temperature:** `sensor.mannito_temperature`
- **Humidity:** `sensor.mannito_humidity`  
- **CO2 Level:** `sensor.mannito_co2`
- **pH Level:** `sensor.mannito_ph`
- **Conductivity:** `sensor.mannito_conductivity`
- **Water Flow:** `sensor.mannito_water_flow`
- **Water Level:** `sensor.mannito_water_level`

## 🔌 API Reference

For developers and advanced users, the integration uses these REST API endpoints:

### Device Control
```http
GET  http://{DEVICE_HOST}/api/device/{COMPONENT_NAME}/state
POST http://{DEVICE_HOST}/api/device/{COMPONENT_NAME}/state/{true|false}
POST http://{DEVICE_HOST}/api/device/{COMPONENT_NAME}/speed/{SPEED}
```

### Configuration
```http
GET http://{DEVICE_HOST}/api/device/config
```

### Authentication
The API supports optional HTTP Basic Authentication for secure access.

## 🛠️ Troubleshooting

### Controller Not Found

**Symptoms:** Integration cannot discover or connect to your controller

**Solutions:**
1. **Verify network connectivity** - Ensure controller and Home Assistant are on the same network
2. **Check IP address** - Try manual configuration with the controller's IP
3. **Firmware compatibility** - Verify your controller firmware supports the required API endpoints
4. **Firewall settings** - Ensure ports are not blocked between devices

### Authentication Issues

**Symptoms:** "Invalid credentials" or authentication errors

**Solutions:**
1. **Verify credentials** - Double-check username and password
2. **Update firmware** - Ensure controller firmware is current
3. **Check documentation** - Consult your controller's authentication requirements
4. **Reset credentials** - Try resetting authentication on the controller

### Entities Not Updating

**Symptoms:** Device states don't reflect actual controller status

**Solutions:**
1. **Check network stability** - Verify consistent connectivity
2. **Restart integration** - Remove and re-add the integration
3. **Review logs** - Check Home Assistant logs for error messages
4. **Verify API compatibility** - Ensure controller API version is supported

### Performance Issues

**Symptoms:** Slow response times or delays

**Solutions:**
1. **Network optimization** - Use wired connections when possible
2. **Reduce polling frequency** - Adjust update intervals if needed
3. **Controller resources** - Ensure controller isn't overloaded
4. **Home Assistant performance** - Monitor system resources

## 🔮 Current Limitations & Future Plans

### Current Limitations
- **Local network only** - Requires direct network access to controller
- **Single controller support** - One controller per integration instance
- **Polling-based updates** - Real-time push notifications not yet supported

### Planned Features
- **☁️ Cloud Integration** - Remote access and monitoring capabilities
- **💡 Dedicated Lighting Control** - Full spectrum LED lighting management
- **📱 Mobile Push Notifications** - Real-time alerts and status updates
- **📊 Advanced Analytics** - Historical data analysis and reporting
- **🔄 Webhook Support** - Real-time push notifications from controller
- **🏗️ Multi-controller Support** - Manage multiple controllers simultaneously

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Reporting Issues
- **Use the issue tracker** for bugs and feature requests
- **Provide detailed information** about your setup and problem
- **Include logs** when reporting bugs

### Development
- **Fork the repository** and create feature branches
- **Follow coding standards** and include tests
- **Submit pull requests** with clear descriptions

### Testing
- **Test with different controller versions** and configurations
- **Report compatibility issues** with specific firmware versions
- **Share your automation examples** with the community

## 📞 Support & Community

### Documentation
- **Integration Documentation:** This README and inline code documentation
- **Home Assistant Docs:** [Home Assistant Integration Documentation](https://developers.home-assistant.io/)
- **Controller Documentation:** Consult your Mannito Farming controller manual

### Community Support
- **GitHub Issues:** [Report bugs and request features](https://github.com/mannito-farming-solutions/mannito-farming-integration/issues)
- **Discussions:** Share experiences and get help from other users
- **Home Assistant Community:** [Home Assistant Community Forum](https://community.home-assistant.io/)

### Commercial Support
For commercial deployments or advanced support needs, contact Mannito Farming Solutions directly.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Home Assistant Community** - For the excellent platform and development tools
- **Mannito Farming Solutions** - For creating innovative agricultural automation systems
- **Contributors** - Everyone who has contributed code, testing, and feedback

---

**Happy Growing! 🌱**

*Transform your agricultural automation with the power of Home Assistant integration.*
