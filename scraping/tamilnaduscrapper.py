import requests
import pandas as pd
import time
from datetime import datetime

# Google Places API Key (Replace with your API Key)
API_KEY = "Censored"

# List of districts in Jammu & Kashmir and Ladakh with approximate coordinates
LOCATIONS = {
    "Jammu & Kashmir": {
        "Anantnag": ["33.7304,75.1490"],
        "Bandipora": ["34.5043,74.6864"],
        "Baramulla": ["34.2011,74.3636"],
        "Budgam": ["34.0209,74.7201"],
        "Doda": ["33.1484,75.5473"],
        "Ganderbal": ["34.2266,74.7713"],
        "Jammu": ["32.7266,74.8570"],
        "Kathua": ["32.3865,75.5189"],
        "Kishtwar": ["33.3113,75.7660"],
        "Kulgam": ["33.6442,75.0194"],
        "Kupwara": ["34.5290,74.2569"],
        "Poonch": ["33.7703,74.0924"],
        "Pulwama": ["33.8760,74.8977"],
        "Rajouri": ["33.3756,74.3124"],
        "Ramban": ["33.2457,75.2390"],
        "Reasi": ["33.0807,74.8370"],
        "Samba": ["32.5667,75.1170"],
        "Shopian": ["33.7197,74.8357"],
        "Srinagar": ["34.0837,74.7973"],
        "Udhampur": ["32.9230,75.1353"]
    },
    "Ladakh": {
        "Leh": ["34.1642,77.5848"],
        "Kargil": ["34.5544,76.1349"]
    }
}

# Tourist categories and keywords
CATEGORIES = {
    "parks": "parks",
    "museum": "museum",
    "waterfalls": "waterfalls",
    "beaches": "beaches",
    "zoo": "zoo",
    "temples": "temple",
    "hills": "hill",
    "attraction": "tourist attraction",
}

# Function to determine peak season for a category
def get_peak_season(category):
    peak_seasons = {
        "parks": "Spring",
        "museum": "Winter",
        "waterfalls": "Monsoon",
        "beaches": "Summer",
        "zoo": "Winter",
        "temples": "All Seasons",
        "hills": "Winter",
        "attraction": "All Seasons",
    }
    return peak_seasons.get(category, "Unknown")

def get_places_data(api_key, location, radius, keyword, category, state, district):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "key": api_key,
        "location": location,
        "radius": radius,
        "keyword": keyword,
    }
    places = []

    while True:
        response = requests.get(url, params=params)
        data = response.json()

        if "results" in data:
            for place in data["results"]:
                spot_id = place.get("place_id")
                spot_name = place.get("name")
                latitude = place["geometry"]["location"].get("lat")
                longitude = place["geometry"]["location"].get("lng")
                rating = place.get("rating", "No rating")
                rating_count = place.get("user_ratings_total", 0)
                categories = ", ".join(place.get("types", []))
                date = datetime.now().strftime("%Y-%m-%d")

                places.append({
                    "Name": spot_name,
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Rating": rating,
                    "Categories": categories,
                    "Keyword": category,
                    "State": state,
                    "Season": get_peak_season(category),
                    "District": district,
                    "Visitors Count of Ratings": rating_count,
                })

        # Check for additional pages
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
        
        params["pagetoken"] = next_page_token
        time.sleep(2)  # Delay to avoid rate limiting

    return places

# Function to fetch all places for Jammu & Kashmir and Ladakh
def fetch_all_tourist_places(api_key, locations, categories):
    all_places = []
    for state, districts in locations.items():
        for district, location_list in districts.items():
            print(f"Fetching places for {district}, {state}...")

            for location in location_list:
                for category, keyword in categories.items():
                    print(f"  Category: {category} at {location}")
                    places = get_places_data(api_key, location, radius=50000, keyword=keyword, category=category, state=state, district=district)

                    all_places.extend(places)

    return pd.DataFrame(all_places)

if __name__ == "__main__":
    df = fetch_all_tourist_places(API_KEY, LOCATIONS, CATEGORIES)

    # Save data to CSV
    df.to_csv("jammu_kashmir_ladakh_tourist_places.csv", index=False)
    print("Tourist places data saved to 'jammu_kashmir_ladakh_tourist_places.csv'.")
