import math
from Tracking.models import GeoFencing,DangerZone

def check_geofence_breach(incoming_lat, incoming_lng):
    # 1. Fetch all active geofences
    fences = GeoFencing.objects.filter(is_active=True)
    
    breached_fences = []
    R = 6371000  # Earth's radius in meters

    for fence in fences:
        # Haversine Formula
        phi1, phi2 = math.radians(fence.latitude), math.radians(incoming_lat)
        d_phi = math.radians(incoming_lat - fence.latitude)
        d_lambda = math.radians(incoming_lng - fence.longitude)

        a = math.sin(d_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c

        # If the distance is GREATER than the radius, they are outside this specific fence
        if distance > fence.radius:
            breached_fences.append({
                'sos':'GeoFence'
            })

    return breached_fences # Returns a list of all fences the user is currently "outside" of



def check_danger_zone_entry(incoming_lat, incoming_lng):
    # Fetch all active danger zones
    danger_zones = DangerZone.objects.filter(is_active=True)
    active_violations = []
    R = 6371000 # Earth's radius in meters

    for zone in danger_zones:
        # Convert coordinates to radians
        phi1 = math.radians(zone.latitude)
        phi2 = math.radians(incoming_lat)
        d_phi = math.radians(incoming_lat - zone.latitude)
        d_lambda = math.radians(incoming_lng - zone.longitude)

        # Haversine Formula
        a = math.sin(d_phi / 2)**2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(d_lambda / 2)**2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        # ALERT: Triggered if distance is LESS than the radius (User is inside)
        if distance <= zone.radius:
            active_violations.append({
                'sos':"DangerZone"
            })

    return active_violations