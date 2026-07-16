# 🎛️ Raspberry Pi Fan Controller with MQTT Telemetry

A lightweight, robust Python daemon that runs as a system service on a Raspberry Pi. It monitors CPU core temperature, triggers a cooling fan via GPIO, and streams real-time state and temperature telemetry to Home Assistant via MQTT.

## 🚀 Features
* **Automated Thermal Control:** Smart fan triggers based on high/low threshold limits.
* **Resilient MQTT Engine:** Uses native Paho-MQTT reconnect protocols to survive Wi-Fi drops and Home Assistant restarts.
* **Continuous State Telemetry:** Streams updates continuously (even when the fan is idle or off) so your Home Assistant dashboard never goes stale.

---

## 🛠️ Installation & Setup

### 1. Clone & Configure
Clone this repository to your Raspberry Pi:
```bash
git clone [https://github.com/YOUR_USERNAME/rpi-mqtt-fancontrol.git](https://github.com/YOUR_USERNAME/rpi-mqtt-fancontrol.git)
cd rpi-mqtt-fancontrol
```

Copy the template configuration file to create your active configuration:
```bash
cp config.py.example config.py
```

Open `config.py` and fill in your MQTT broker details, credentials, and GPIO configurations:
```bash
nano config.py
```

### 2. Install Dependencies
Install the required Python libraries for GPIO control and MQTT communication:
```bash
pip3 install gpiozero paho-mqtt
```

### 3. Deploy as a Background System Service
To ensure the script runs continuously in the background and automatically starts when the Raspberry Pi boots up, configure it as a systemd service:

```bash
# Copy the script, config, and systemd unit files to system directories
sudo cp fancontrol.py config.py /usr/local/bin/
sudo cp fan_control.service /etc/systemd/system/

# Reload systemd to recognize the new service configuration
sudo systemctl daemon-reload

# Enable the service to launch on system boot
sudo systemctl enable fan_control.service

# Start the background daemon immediately
sudo systemctl start fan_control.service
```

### 4. Monitor Live Status
To check if the daemon is active and verify it is successfully sending telemetry:
```bash
sudo systemctl status fan_control.service
```

To watch the live execution logs and MQTT transmission events in real-time:
```bash
sudo journalctl -u fan_control.service -f
```

---

## 🏠 Home Assistant Integration

### Backend Configuration (`configuration.yaml`)
Add these entries to map the incoming MQTT JSON streams to native Home Assistant entities:

```yaml
mqtt:
  binary_sensor:
    - name: "Bobby Fan Main"
      state_topic: "rpi/fan"
      value_template: "{{ value_json.status }}"
      payload_on: "on"
      payload_off: "off"
      unique_id: "bobby_rpi_fan_v3"

  sensor:
    - name: "Bobby Temperature"
      state_topic: "rpi/fan"
      value_template: "{{ value_json.temp }}"
      unit_of_measurement: "°C"
      device_class: temperature
      unique_id: "bobby_cpu_temp_v3"
```

### Frontend Dashboard (`Mushroom Template Card`)
Add a Mushroom card to your dashboard to display the dynamic state:

```yaml
type: custom:mushroom-template-card
primary: Bobby Fan
secondary: >-
  Status: {{ states('binary_sensor.bobby_fan_main') | title }} | {{ states('sensor.bobby_temperature') }}°C
icon: >-
  {% if is_state('binary_sensor.bobby_fan_main', 'on') %} mdi:fan {% else %} mdi:fan-off {% endif %}
icon_color: >-
  {% if is_state('binary_sensor.bobby_fan_main', 'on') %} green {% else %} blue {% endif %}
entity: binary_sensor.bobby_fan_main
tap_action:
  action: more-info
```