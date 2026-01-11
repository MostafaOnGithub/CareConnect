import os
import django
import json
import paho.mqtt.client as mqtt

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareConnect.settings')
django.setup()

from Devices.models import Device, DeviceLocationLog

# Configuration
STATIC_SERIAL = "00000000"
BROKER_IP = "192.168.1.101"
MQTT_TOPIC = "esp32/gps"  # Change this to match your actual topic

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connected successfully to {BROKER_IP}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    try:

        payload = json.loads(msg.payload.decode())
        lat = payload.get('lat')
        lng = payload.get('lng') or payload.get('long') # Handles both lng/long

        device, created = Device.objects.get_or_create(serial_number=STATIC_SERIAL)
        
        if created:
            print(f"Created new device record for serial: {STATIC_SERIAL}")

        # Save to your DB
        DeviceLocationLog.objects.create(
            device=device,
            latitude=lat,
            longitude=lng
        )
        print(f"Recorded: Lat {lat}, Lng {lng} for device {STATIC_SERIAL}")
        
    except Exception as e:
        print(f"Error: {e} | Raw Message: {msg.payload}")

# 3. Initialize Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

print(f"Connecting to MQTT Broker at {BROKER_IP}...")
client.connect(BROKER_IP, 1883, 60)

client.loop_forever()