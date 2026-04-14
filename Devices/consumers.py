import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SOSConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "sos_alerts"
        # Join the emergency group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # This method is called by your Paho script via group_send
    async def send_sos_notification(self, event):
        # Send message to the browser WebSocket
        await self.send(text_data=json.dumps({
            'device_id': event['device_id'],
            'lat': event['lat'],
            'lng': event['lng'],
            'status': 'ALARM'
        }))