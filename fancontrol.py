import os
import time
import json
from gpiozero import OutputDevice
import paho.mqtt.client as paho

# Import custom configuration
try:
    import config
except ImportError:
    print("[ERROR] config.py file not found! Please copy config.py.example to config.py and fill in your details.")
    exit(1)

# Configuration parameters from config.py
BROKER = config.MQTT_BROKER
MQTT_USER = config.MQTT_USER
MQTT_PASS = config.MQTT_PASSWORD
GPIO_PIN = config.GPIO_PIN
ON_THRESHOLD = config.ON_THRESHOLD
OFF_THRESHOLD = config.OFF_THRESHOLD
SLEEP_INTERVAL = config.SLEEP_INTERVAL

def get_temp():
    """Reads the Raspberry Pi CPU temperature."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000.0
        return temp
    except Exception as e:
        print(f"[ERROR] Could not read CPU temperature: {e}")
        return 0.0

def on_message(client, userdata, message):
    pass

if __name__ == '__main__':
    client = paho.Client("bobby-fan")
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_message = on_message

    fan = OutputDevice(GPIO_PIN)

    # Start the background loop immediately
    client.loop_start() 

    # Attempt initial connection
    try:
        client.connect(BROKER, port=1883, keepalive=60)
    except Exception as e:
        print(f"[WARN] Initial connection failed: {e}. Will retry automatically.")

    while True:
        temp = get_temp()
        
        # Start the fan if temperature limit is reached
        if temp > ON_THRESHOLD and not fan.value:
            fan.on()

        # Stop the fan if it dropped below threshold
        elif fan.value and temp < OFF_THRESHOLD:
            fan.off()

        # ALWAYS read actual hardware state
        status_text = "on" if fan.value else "off"

        # Dynamically publish if connected
        if client.is_connected():
            try:
                payload = json.dumps({"status": status_text, "temp": round(temp, 1)})
                client.publish("rpi/fan", payload, qos=1)
            except Exception as e:
                print(f"[ERROR] Failed to publish: {e}")
        else:
            try:
                client.reconnect()
            except:
                pass

        time.sleep(SLEEP_INTERVAL)