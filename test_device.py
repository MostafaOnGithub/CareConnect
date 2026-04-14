import paho.mqtt.client as mqtt
import json
import time

BROKER_IP = "127.0.0.1" # Same as your listener
TOPIC = "esp32/gps"

client = mqtt.Client()
client.connect(BROKER_IP, 1883, 60)

print("Starting Mock Device... Sending data every 5 seconds.")

try:
    count = 0
    while True:
        count += 1
        # Every 4th message, make it an SOS
        is_sos = True if count % 4 == 0 else False
        
        payload = {
            "lat": 30.0444,
            "lng": 31.2357,
            "sos": is_sos
        }
        
        client.publish(TOPIC, json.dumps(payload))
        print(f"Sent: {payload}")
        time.sleep(5)
except KeyboardInterrupt:
    print("Stopped.")