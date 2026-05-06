import requests

def search_doctors(specialty: str, location: str, limit: int = 20):
    """
    Search for doctors/clinics/hospitals using OpenStreetMap Nominatim API.
    Tries multiple query strategies to get the best results.
    """

    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Strategy 1: specialty + doctor + location
    # Strategy 2: specialty + clinic + location  
    # Strategy 3: hospital + location (broad fallback)
    queries = [
        f"{specialty} doctor {location}",
        f"{specialty} clinic {location}",
        f"{specialty} hospital {location}",
        f"hospital {location}",
    ]

    seen_names = set()
    doctors = []

    for query in queries:
        if len(doctors) >= limit:
            break

        params = {
            "q": query,
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=8)
            if response.status_code != 200:
                continue

            for place in response.json():
                if len(doctors) >= limit:
                    break

                name = place.get("display_name", "N/A").split(",")[0].strip()

                # De-duplicate
                if name in seen_names:
                    continue
                seen_names.add(name)

                doctors.append({
                    "name": name,
                    "full_address": place.get("display_name", "N/A"),
                    "latitude": float(place.get("lat", 0)),
                    "longitude": float(place.get("lon", 0)),
                    "type": place.get("type", "N/A"),
                    "specialty": specialty,
                })

        except Exception:
            continue

    return doctors

def search_pharmacies(location: str, limit: int = 20):
    """
    Search for pharmacies using OpenStreetMap Nominatim API.
    """

    url = "https://nominatim.openstreetmap.org/search"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    queries = [
        f"pharmacy {location}",
        f"chemist {location}",
        f"medical store {location}",
        f"drugstore {location}"
    ]

    seen_names = set()
    pharmacies = []

    for query in queries:
        if len(pharmacies) >= limit:
            break

        params = {
            "q": query,
            "format": "json",
            "limit": limit,
            "addressdetails": 1,
        }

        try:
            response = requests.get(url, params=params, headers=headers, timeout=8)
            if response.status_code != 200:
                continue

            for place in response.json():
                if len(pharmacies) >= limit:
                    break

                name = place.get("display_name", "N/A").split(",")[0].strip()

                if name in seen_names:
                    continue
                seen_names.add(name)

                pharmacies.append({
                    "name": name,
                    "full_address": place.get("display_name", "N/A"),
                    "latitude": float(place.get("lat", 0)),
                    "longitude": float(place.get("lon", 0)),
                    "type": place.get("type", "Pharmacy")
                })

        except Exception:
            continue

    return pharmacies

