import os
import django
import json
import paho.mqtt.client as mqtt
import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareConnect.settings')
django.setup()

from Devices.models import Device,SosEvent
from Tracking.models import DeviceLocationLog

# Configuration
STATIC_SERIAL = "00000000"
BROKER_IP = "127.0.0.1"
MQTT_TOPIC = "esp32/gps"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to {BROKER_IP}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Connection failed, code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        lat = payload.get('lat')
        lng = payload.get('lng') or payload.get('long')
        # Check if the ESP32 sent an SOS flag
        is_sos = payload.get('sos', False) 

        device, created = Device.objects.get_or_create(serial_number=STATIC_SERIAL)

        # Save to DB
        log_entry = DeviceLocationLog.objects.create(
            device=device,
            latitude=lat,
            longitude=lng
        )
        print(f"📍 Data Saved: {lat}, {lng}")

        # --- THE ALARM LOGIC ---
        if is_sos:
            sos = SosEvent.objects.create(device=device)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "sos_alerts", 
                {
                    "type": "send_sos_notification",
                    "device_id": STATIC_SERIAL,
                    "lat": lat,
                    "lng": lng,
                }
            )
            print("🚨 SOS BROADCAST SENT!")

    except Exception as e:
        print(f"⚠️ Error in on_message: {e}")

# 3. Initialize Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# --- THE LOOP ---
while True:
    try:
        print(f"🔄 Connecting to Broker at {BROKER_IP}...")
        client.connect(BROKER_IP, 1883, 60)
        
        # This line below IS the loop. 
        # It blocks here and runs forever until the script is killed or crashes.
        client.loop_forever() 
        
    except Exception as e:
        print(f"💥 Script crashed: {e}. Restarting in 5 seconds...")
        time.sleep(5)