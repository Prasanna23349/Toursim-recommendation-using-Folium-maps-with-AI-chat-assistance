import requests
import pandas as pd
import time
from datetime import datetime

def get_places_data(api_key, location, radius, keyword, category):
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
                categories = ", ".join(place.get("types", []))
                date = datetime.now().strftime("%Y-%m-%d")


                places.append({
                    "spot_id": spot_id,
                    "spot_name": spot_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "category": categories,
                    "date": date,
                    "rating":rating,
                })
        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
        params["pagetoken"] = next_page_token
        time.sleep(2)
    return places

def fetch_all_states_tourist_places(api_key, states, categories):
    all_places = []
    for state, location in states.items():
        print(f"Fetching places for {state}...")
        for category, keyword in categories.items():
            print(f"  Category: {category}")
            places = get_places_data(api_key, location, radius=50000, keyword=keyword, category=category)
            for place in places:
                place["state"] = state
            all_places.extend(places)
    return pd.DataFrame(all_places)

if __name__ == "__main__":
    API_KEY = ""

    # Dictionary of Indian states and representative lat-long (major cities)
    STATES = {
        "Delhi": "28.6139,77.2090",
        "Maharashtra": "19.0760,72.8777",
        "Tamil Nadu": "13.0827,80.2707",
        "Karnataka": "12.9716,77.5946",
        "Rajasthan": "26.9124,75.7873",
        "Uttar Pradesh": "26.8467,80.9462",
        "Kerala": "8.5241,76.9366",
        "West Bengal": "22.5726,88.3639",
        "Gujarat": "23.0225,72.5714",
        "Andhra Pradesh": "15.9129,79.7400",
        "Himachal Pradesh": "31.1048,77.1734",
        "Madhya Pradesh": "23.2599,77.4126",
        "Goa": "15.2993,74.1240",
        "Bihar": "25.5941,85.1376",
        "Punjab": "30.7333,76.7794",
        "Haryana": "28.7041,77.1025",
        "Assam": "26.2006,92.9376",
        "Jharkhand": "23.6102,85.2799",
        "Chhattisgarh": "21.2787,81.8661",
        "Uttarakhand": "30.0668,79.0193",
        "Odisha": "20.2961,85.8245",
        "Telangana": "17.3850,78.4867",
        "Puducherry": "11.9416,79.8083",
        "Tripura": "23.8315,91.2868",
        "Meghalaya": "25.5788,91.8933",
        "Manipur": "24.8170,93.9368",
        "Nagaland": "25.6747,94.1086",
        "Arunachal Pradesh": "27.0844,93.6053",
        "Mizoram": "23.1645,92.9376",
        "Sikkim": "27.5330,88.5122",
        "Andaman and Nicobar Islands": "11.6670,92.7356",
        "Chandigarh": "30.7333,76.7794",
        "Dadra and Nagar Haveli and Daman and Diu": "20.3974,72.8328",
        "Lakshadweep": "10.5667,72.6417",
        "Jammu and Kashmir": "34.0837,74.7973",
        "Ladakh": "34.2268,77.5619",
    }

    CATEGORIES = {
        "attraction": "attraction",
        "beaches": "beaches",
        "waterfalls": "waterfalls",
        "parks": "parks",
        "museum": "museum",
    }

    df = fetch_all_states_tourist_places(API_KEY, STATES, CATEGORIES)

    df.to_csv("tourist_places_india_with_categories2.csv", index=False)
    print("Tourist places data saved to 'tourist_places_india_with_categories.csv'.")
