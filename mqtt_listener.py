import os
import django
import json
import paho.mqtt.client as mqtt
import time
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from zone_checker import check_geofence_breach,check_danger_zone_entry
# 1. Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareConnect.settings')
django.setup()

from Devices.models import Device,SosEvent
from Tracking.models import DeviceLocationLog
from Biometrics.models import BiometricReading

# Configuration
STATIC_SERIAL = "00000000"
BROKER_IP = "192.168.1.102"
MQTT_TOPIC = "esp32/"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ Connected to {BROKER_IP}")
        client.subscribe(MQTT_TOPIC)
    else:
        print(f"❌ Connection failed, code {rc}")

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        # GPS Data
        lat = payload.get('lat')
        lng = payload.get('lng') or payload.get('long')
        # Biometric Data
        bpm = payload.get('bpm')
        # Check if the ESP32 sent an SOS flag
        is_sos = payload.get('sos')

        device, created = Device.objects.get_or_create(serial_number=STATIC_SERIAL)

        # Save to DB


        log_entry = DeviceLocationLog.objects.create(
            device=device,
            latitude=lat,
            longitude=lng
        )
        print(f"📍 Data Saved: {lat}, {lng}")

        if bpm is not None:
            BiometricReading.objects.create(heart_rate=bpm,device=device)


        # --- THE ALARM LOGIC ---
        if is_sos :
            if sos == "button" :
                sos = SosEvent.objects.create(device=device,sos_types="button")
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "sos_alerts", 
                    {
                        "type": "send_sos_notification_through_button",
                        "device_id": STATIC_SERIAL,
                        "lat": lat,
                        "lng": lng,
                    }
                )
                print("🚨 SOS BROADCAST SENT THROUGH BUTTON!")
            else :
                sos = SosEvent.objects.create(device=device,sos_types="mpu")
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "sos_alerts", 
                    {
                        "type": "send_sos_notification_through_mpu",
                        "device_id": STATIC_SERIAL,
                        "lat": lat,
                        "lng": lng,
                    }
                )
                print("🚨 SOS BROADCAST SENT THROUGH MPU!")
        geoSos = check_geofence_breach(lat,lng)
        dangerZoneSos = check_danger_zone_entry(lat,lng)
        if geoSos:
            geoSos = SosEvent.objects.create(device=device,sos_types="geofencing")
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "sos_alerts", 
                {
                    "type": "send_sos_notification_out_of_fence",
                    "device_id": STATIC_SERIAL,
                    "lat": lat,
                    "lng": lng,
                }
            )
        if dangerZoneSos:
            dangerZoneSos = SosEvent.objects.create(device=device,sos_types="dangerzone")
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "sos_alerts", 
                {
                    "type": "send_sos_notification_in_danger_area",
                    "device_id": STATIC_SERIAL,
                    "lat": lat,
                    "lng": lng,
                }
            )

        



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