# 📦 **Safety Tracker System – README**

A full IoT-based safety tracking system consisting of:

* **Local Django Server** (backend)
* **Mobile Application** (client)
* **ESP32-Based Tracking Device** (hardware)

This system provides real-time location tracking, daily route logging, biometric monitoring, alarm control, camera streaming activity log, and geofencing/danger zone alerts.

---

# 🚀 **System Overview**

```
ESP32 DEVICE  →  Django Local Server  →  Mobile App
```

### ✔ Device (ESP32 / MCU)

* Sends GPS coordinates
* Sends biometric data (heart rate, Spo2)
* Receives camera activation commands
* Sends alerts

### ✔ Django Server

* Stores all device data
* Provides REST API for the app
* Performs geofence + danger zone checks
* Reconstructs full daily routes
* Sends commands back to the device

### ✔ Mobile App

* Displays live location
* Shows the full route of the day
* Shows heart rate/Spo2 in real time
* Manages alarms & device settings
* Sets geofencing and danger zones

---

# 📁 **Project Structure**

```
project_root/
│
├── config/                # Django settings and routing
│
├── apps/
│   ├── users/             # Authentication & user management
│   ├── devices/           # Device registration & linking
│   ├── tracking/          # GPS logs, routes, geofencing
│   ├── biometrics/        # Heart rate, SpO2 readings
│   ├── camera/            # Stream logs & camera commands
│   ├── alarms/            # Alarm storage & control
│
├── api/                   # Django REST Framework routes
│
├── requirements.txt
├── README.md
└── manage.py
```

This modular structure keeps the system clean, scalable, and easy to maintain.

---

# 🧩 **Core Features**

### ⭐ **1. Live Tracking**

* Device sends latitude/longitude
* Stored in `DeviceLocationLog`
* App requests `/api/tracking/live/`

### ⭐ **2. Full Route History**

Every GPS point is stored.
The app can request the entire route for the day:

```
GET /api/tracking/route/today/?device_id=1
```

Returned as sorted coordinates → used to draw a polyline on the map.

---

# 🧭 **3. Geofencing & Danger Zones**

Users can configure:

* Allowed radius (safe zone)
* Restricted areas (danger zones)

The server checks each incoming location and triggers alerts when needed.

---

# ❤️ **4. Biometric Monitoring**

Device sends:

* Heart rate
* Spo2 level

Django saves to `BiometricReading`.
The app fetches both live and historical data.

---

# 📷 **5. Camera Control**

Server logs when the camera is:

* Activated (currently shuttering)
* Deactivated

The server can also send commands back to the device.

---

# ⏰ **6. Alarms**

Users can set alarms routed to devices.

Stored in the `Alarm` model and synced with device/app.

---

# 🗄️ **Database Schema Summary**

### Key Tables:

* `Users`
* `Devices`
* `UserDeviceLink`
* `DeviceLocationLog` (daily route)
* `BiometricReading`
* `GeoFencing`
* `DangerZone`
* `CameraStream`
* `Alarm`

All location logs include a timestamp → allowing perfect path reconstruction.

---

# 🔌 **Device → Server Communication**

### 📡 HTTP POST Example

```
POST /api/tracking/location/

{
  "device_serial": "ABC12345",
  "latitude": 30.0452,
  "longitude": 31.2361
}
```

### MQTT Support

Topics like:

```
tracking/device/ABC123/location
tracking/device/ABC123/biometrics
```

MQTT is recommended for real-time performance.

---

# 📱 **Mobile App → Server Communication**

### GET daily route:

```
GET /api/tracking/route/today/?device_id=1
```

### GET live biometrics:

```
GET /api/biometrics/live/?device_id=1
```

### POST set geofence:

```
POST /api/tracking/geofence/create/
```

### POST start camera:

```
POST /api/camera/start/
```

---

# 🧪 **Testing with Sample Data**

Insert a test device:

```bash
python manage.py shell
```

```python
from apps.devices.models import Device
Device.objects.create(serial_number="TEST001")
```

Now you can test location API routes.

---

# 📌 **Future Improvements (Currently on dev phase)**

* MQTT live streaming
* WebSocket updates for live tracking
* AI anomaly detection (irregular movement/biometrics)
* Battery monitoring
* Emergency SOS channel

---

# 📞 **Support**

If you need help integrating the ESP32, Android/iOS app, or extending Django modules, please feel free to open an issue or contact the developer.

---

