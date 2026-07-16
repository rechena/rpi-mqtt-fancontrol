# 🎛️ Raspberry Pi Fan Controller with MQTT Telemetry

A lightweight, robust Python daemon that runs as a system service on a Raspberry Pi. It monitors CPU core temperature, triggers a cooling fan via GPIO, and streams real-time state and temperature telemetry to Home Assistant via MQTT.

## 🚀 Features
* **Automated Thermal Control:** Smart fan triggers based on high/low threshold limits.
* **Resilient MQTT Engine:** Uses native Paho-MQTT reconnect protocols to survive Wi-Fi drops and Home Assistant restarts.
* **Continuous State Telemetry:** Streams updates continuously (even when the fan is idle or off) so your Home Assistant dashboard never goes stale.

---

## 🔌 Hardware & Physical Setup

This project uses a standard 5V or 12V brushless DC cooling fan controlled via a **GPIO pin** on the Raspberry Pi. 

> ⚠️ **IMPORTANT:** Do not connect the fan's power wire directly to a Raspberry Pi GPIO pin! GPIO pins can only safely output about 16mA of current, whereas a fan requires 100mA+. Always use a **transistor (like a PN2222)** or a **relay module** as a switch to protect your Pi.

### Typical Wiring Diagram (Using an NPN Transistor)

```text
       [5V or 3.3V Pin] --------------> Fan (+)
                                         
       [GPIO Pin 14] ----[ 1kΩ Resistor ]----> Base (Middle Pin of Transistor)
                                         
       [GND Pin] ----------------------------> Emitter (Right Pin of Transistor)
                                         
       Fan (-) ------------------------------> Collector (Left Pin of Transistor)
```

### Raspberry Pi Pin Reference Table

By default, this script is configured to use physical pinouts based on the standard **BCM (Broadcom) numbering**:

| Component | Physical Pin | BCM Pin | Description |
| :--- | :--- | :--- | :--- |
| **Fan VCC (+)** | Pin 2 or 4 | **5V Power** | Supplies power to the fan. (Use Pin 1 for 3.3V fans). |
| **Fan GND (-)** | Pin 6 (or any GND) | **Ground** | System ground. |
| **Control Signal** | Pin 8 | **GPIO 14 (TXD)** | Sends the ON/OFF signal to the transistor base or relay trigger. |

*(Note: You can change the control pin to any free GPIO by editing the `GPIO_PIN` variable in your custom `config.py` file).*

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
vim config.py
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
    - name: "rpi Fan Main"
      state_topic: "rpi/fan"
      value_template: "{{ value_json.status }}"
      payload_on: "on"
      payload_off: "off"
      unique_id: "rpi_rpi_fan_v3"

  sensor:
    - name: "rpi Temperature"
      state_topic: "rpi/fan"
      value_template: "{{ value_json.temp }}"
      unit_of_measurement: "°C"
      device_class: temperature
      unique_id: "rpi_cpu_temp_v3"
```

### Frontend Dashboard (`Mushroom Template Card`)
Add a Mushroom card to your dashboard to display the dynamic state:

```yaml
type: custom:mushroom-template-card
primary: rpi Fan
secondary: >-
  Status: {{ states('binary_sensor.rpi_fan_main') | title }} | {{ states('sensor.rpi_temperature') }}°C
icon: >-
  {% if is_state('binary_sensor.rpi_fan_main', 'on') %} mdi:fan {% else %} mdi:fan-off {% endif %}
icon_color: >-
  {% if is_state('binary_sensor.rpi_fan_main', 'on') %} green {% else %} blue {% endif %}
entity: binary_sensor.rpi_fan_main
tap_action:
  action: more-info
```
