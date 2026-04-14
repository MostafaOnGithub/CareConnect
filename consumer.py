import os
import django
import asyncio
from channels.layers import get_channel_layer

# 1. Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CareConnect.settings')
django.setup()

async def catch_sos():
    channel_layer = get_channel_layer()
    # Create a temporary channel for this test script
    test_channel = await channel_layer.new_channel()
    # Join the same group your listener sends to
    await channel_layer.group_add("sos_alerts", test_channel)
    
    print("👂 Listening for the Channel Layer broadcast...")
    
    while True:
        # Wait for the message to arrive
        message = await channel_layer.receive(test_channel)
        print(f"🎯 CAUGHT IT! Channel Layer received: {message}")

if __name__ == "__main__":
    asyncio.run(catch_sos())