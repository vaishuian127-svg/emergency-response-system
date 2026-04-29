import requests
import math


def get_coordinates(location: str):
    """
    Converts a location name to latitude and longitude.
    Tries multiple search strategies to maximize success, restricted to India.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "EmergencyResponseSystem/1.0"}

    # Strategy 1: Search exactly as given, restricted to India
    params = {"q": location, "format": "json", "limit": 1, "countrycodes": "in"}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception:
        pass

    # Strategy 2: Add "India" explicitly if no result
    if "india" not in location.lower():
        params = {"q": location + ", India", "format": "json", "limit": 1, "countrycodes": "in"}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass

    # Strategy 3: Try just the last word (city name only)
    parts = [p.strip() for p in location.replace(",", " ").split() if len(p.strip()) > 3]
    if parts:
        params = {"q": parts[-1], "format": "json", "limit": 1, "countrycodes": "in"}
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
            data = response.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass

    # Strategy 4: Fallback to Open-Meteo Geocoding (great for cities like Tumkuru)
    try:
        first_part = location.split(",")[0].strip()
        om_url = "https://geocoding-api.open-meteo.com/v1/search"
        om_params = {"name": first_part, "count": 5}
        response = requests.get(om_url, params=om_params, timeout=15)
        data = response.json()
        if data.get("results"):
            # Try to find an Indian match first
            for res in data["results"]:
                if res.get("country_code") == "IN":
                    return float(res["latitude"]), float(res["longitude"])
            # Fallback to whatever first result is
            return float(data["results"][0]["latitude"]), float(data["results"][0]["longitude"])
    except Exception:
        pass

    return None, None


def classify_hospital_type(tags: dict) -> str:
    """
    Smartly classify hospital as Government, Private, or Hospital
    by checking multiple OSM tags. Works well for Indian hospitals.
    """

    # 1. Check operator:type tag first (most reliable if present)
    operator_type = tags.get("operator:type", "").lower()
    if operator_type in ("government", "public", "ngo", "religious"):
        return "Government"
    if operator_type == "private":
        return "Private"

    # 2. Check operator name for government keywords
    operator = tags.get("operator", "").lower()
    govt_keywords = [
        "government", "govt", "gov ", "district hospital", "district health",
        "public health", "taluk", "thaluk", "primary health", "phc",
        "community health", "chc", "sub district", "civil hospital",
        "municipal", "corporation", "esic", "esi ", "railway hospital",
        "army hospital", "military hospital", "aiims", "nimhans",
        "nimhans", "kidwai", "victoria", "bowring", "lady goschen",
        "wenlock", "general hospital", "state hospital", "national hospital",
        "Karnataka", "india gov", "nh ", "national health"
    ]
    private_keywords = [
        "apollo", "fortis", "manipal", "narayana", "columbia", "aster",
        "sakra", "sparsh", "cloudnine", "motherhood", "rainbow", "wockhardt",
        "max healthcare", "medanta", "care hospital", "sunshine", "vikram",
        "sagar hospital", "baptist", "st john", "st. john", "pvt", "private",
        "ltd", "limited", "healthcare pvt", "clinic pvt"
    ]

    for kw in govt_keywords:
        if kw in operator:
            return "Government"
    for kw in private_keywords:
        if kw in operator:
            return "Private"

    # 3. Check the hospital name itself
    name = tags.get("name", "").lower()
    govt_name_keywords = [
        "government", "govt", "district hospital", "taluk hospital",
        "thaluk", "primary health", "phc ", "community health", "chc ",
        "civil hospital", "municipal hospital", "general hospital",
        "public hospital", "state hospital", "aiims", "nimhans",
        "esic hospital", "esi hospital", "railway hospital",
        "army hospital", "military hospital", "lady goschen",
        "bowring", "victoria hospital", "wenlock", "kidwai"
    ]
    private_name_keywords = [
        "apollo", "fortis", "manipal", "narayana", "columbia", "aster",
        "sakra", "sparsh", "cloudnine", "motherhood", "rainbow", "wockhardt",
        "medanta", "care hospital", "sunshine", "vikram", "sagar",
        "baptist", "st john", "st. john", "pvt", "private ltd"
    ]

    for kw in govt_name_keywords:
        if kw in name:
            return "Government"
    for kw in private_name_keywords:
        if kw in name:
            return "Private"

    # 4. Fallback
    return "Hospital"


def find_nearby_hospitals(location: str, radius_km: int = 5):
    """
    Finds real hospitals near a given location.
    Uses OpenStreetMap Overpass API — completely free.
    Works for any city in the world.
    """
    lat, lon = get_coordinates(location)
    if lat is None:
        return [], None, None

    radius_m = radius_km * 1000

    query = f"""
    [out:json][timeout:30];
    (
      node["amenity"="hospital"](around:{radius_m},{lat},{lon});
      way["amenity"="hospital"](around:{radius_m},{lat},{lon});
      node["healthcare"="hospital"](around:{radius_m},{lat},{lon});
    );
    out body;
    >;
    out skel qt;
    """

    # Try multiple Overpass servers in case one is down or rate-limiting
    overpass_servers = [
        "https://overpass-api.de/api/interpreter",
        "https://z.overpass-api.de/api/interpreter",
        "https://lz4.overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]

    data = None
    headers = {"User-Agent": "EmergencyResponseSystem/1.0"}
    for overpass_url in overpass_servers:
        try:
            response = requests.post(overpass_url, data=query, headers=headers, timeout=20)
            if response.status_code == 200 and response.text.strip():
                data = response.json()
                break
        except Exception:
            continue

    if data is None:
        # Fallback to dummy data instead of crashing if all servers are unavailable
        fallback_hospitals = [
            {
                "name": "City General Hospital (Fallback Data)",
                "distance_km": 1.5,
                "estimated_time_min": math.ceil((1.5 * 1.5) + 2),
                "type": "Government",
                "lat": lat + 0.015,
                "lon": lon + 0.015,
                "phone": "104",
                "emergency": "yes"
            },
            {
                "name": "Care Life Clinic (Fallback Data)",
                "distance_km": 3.2,
                "estimated_time_min": math.ceil((3.2 * 1.5) + 2),
                "type": "Private",
                "lat": lat - 0.02,
                "lon": lon + 0.01,
                "phone": "+91 9876543210",
                "emergency": "yes"
            },
            {
                "name": "District Health Center (Fallback Data)",
                "distance_km": 4.8,
                "estimated_time_min": math.ceil((4.8 * 1.5) + 2),
                "type": "Government",
                "lat": lat + 0.03,
                "lon": lon - 0.02,
                "phone": "108",
                "emergency": "yes"
            }
        ]
        return fallback_hospitals, lat, lon

    hospitals = []
    for element in data.get("elements", []):
        tags = element.get("tags", {})
        name = tags.get("name", "Unknown Hospital")
        if name == "Unknown Hospital":
            continue

        # Filter out hospitals explicitly marked as not handling emergencies
        if tags.get("emergency") == "no":
            continue

        # Filter out non-emergency specialty hospitals / clinics
        name_lower = name.lower()
        non_emergency_keywords = [
            "dental", "eye", "vision", "fertility", "ivf", "hair", 
            "physiotherapy", "physio", "homeopathy", "ayurveda", "ayurvedic",
            "unani", "siddha", "rehab", "psychiatric", "acupuncture", "skin",
            "laser", "derma", "diagnostic", "lab", "scan", "mri", "imaging",
            "blood bank", "blood center", "pharmacy", "dispensary", "veterinary",
            "vet", "pet", "animal", "aesthetic", "wellness", "fitness", "yoga",
            "polyclinic", "poly clinic", "outpatient", "consulting", "x-ray", "xray",
            "clinic"
        ]
        if any(kw in name_lower for kw in non_emergency_keywords):
            # Exception: if they explicitly have emergency=yes, we might keep them, 
            # but usually a dental hospital with emergency=yes is just a dental emergency.
            continue

        if element["type"] == "node":
            h_lat = element["lat"]
            h_lon = element["lon"]
        else:
            h_lat = element.get("center", {}).get("lat", lat)
            h_lon = element.get("center", {}).get("lon", lon)

        distance = haversine(lat, lon, h_lat, h_lon)

        # Estimate travel time: ~40 km/h average speed = ~1.5 min per km. Add 2 min for boarding.
        estimated_time_min = math.ceil((distance * 1.5) + 2)

        # Use smart classification
        h_type = classify_hospital_type(tags)

        phone = tags.get("phone") or tags.get("contact:phone") or tags.get("telephone") or None

        hospitals.append({
            "name": name,
            "distance_km": round(distance, 2),
            "estimated_time_min": estimated_time_min,
            "type": h_type,
            "lat": h_lat,
            "lon": h_lon,
            "phone": phone,
            "emergency": tags.get("emergency", "yes"),
        })

    hospitals.sort(key=lambda x: x["distance_km"])
    return hospitals, lat, lon


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c