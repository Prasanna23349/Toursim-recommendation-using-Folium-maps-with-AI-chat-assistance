import pandas as pd
from geopy.distance import geodesic
import folium
import requests
from folium import plugins


data = pd.read_csv("indianspots.csv")
dataset = pd.DataFrame(data)


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


user_location = (12.971318, 79.163892)
radius = 50
category_filter = "temples"
season_filter = "All Seasons"


def filter_by_distance(df, user_location, radius):
    filtered_data = []
    for _, row in df.iterrows():
        spot_location = (row['Latitude'], row['Longitude'])
        distance = geodesic(user_location, spot_location).km
        if distance <= radius:
            filtered_data.append({
                "Name": row['Name'],
                "Latitude": row['Latitude'],
                "Longitude": row['Longitude'],
                "Rating": row['Rating'],
                "Categories": row['Categories'],
                "Season": row['Season'],
                "Distance": distance,
                "Visitors_Count": row.get('Visitors_Count'),
                "Keyword": row.get('Keyword')
            })
    return pd.DataFrame(filtered_data)


def filter_by_category(df, category_filter):
    if category_filter.lower() != "allcategories":
        category = CATEGORIES.get(category_filter.lower(), None)
        if category:
            df = df[df['Categories'].str.contains(category, case=False, na=False)]
    return df


def filter_by_season(df, season_filter):
    if season_filter.lower() != "allseasons":
        df = df[df['Season'].str.lower() == season_filter.lower()]
    return df


def sort_results(df):
    return df.sort_values(by=['Rating', 'Distance'], ascending=[False, True])


def recommend_spots(user_location, radius, category_filter, season_filter, dataset):
    filtered_df = filter_by_distance(dataset, user_location, radius)
    filtered_df = filter_by_category(filtered_df, category_filter)
    filtered_df = filter_by_season(filtered_df, season_filter)
    sorted_df = sort_results(filtered_df)
    return sorted_df


def get_route(user_location, destination):
    osrm_url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{user_location[1]},{user_location[0]};{destination[1]},{destination[0]}?overview=full&geometries=geojson"
    )
    response = requests.get(osrm_url)
    if response.status_code == 200:
        data = response.json()
        coordinates = data['routes'][0]['geometry']['coordinates']
        return [(coord[1], coord[0]) for coord in coordinates]
    return []

def visualize_map_with_chatbot(user_location, recommendations):
    tourist_map = folium.Map(location=user_location, zoom_start=12)

    # Add User's Location
    folium.Marker(
        location=user_location,
        popup="Your Location",
        icon=folium.Icon(color='blue')
    ).add_to(tourist_map)

    # Add Recommended Spots with Routes
    list_items = "" 
    for _, row in recommendations.iterrows():
        destination = (row['Latitude'], row['Longitude'])

        # Add Marker
        folium.Marker(
            location=destination,
            popup=f"<b>{row['Name']}</b><br>Rating: {row['Rating']}<br>Distance: {row['Distance']:.2f} km",
            icon=folium.Icon(color='green')
        ).add_to(tourist_map)

        # Draw route using OSRM
        route = get_route(user_location, destination)
        if route:
            folium.PolyLine(route, color="blue", weight=3, opacity=0.7).add_to(tourist_map)

        list_items += f"""
        <li>
            <b>{row['Name']}</b><br>
            <b>Rating:</b> {row['Rating']}, <b>Distance:</b> {row['Distance']:.2f} km, <b>Visitors:</b> {row['Visitors_Count']}, <b>Keyword:</b> {row['Keyword']}
        </li><hr>
        """

    html = f'''
    <div style="position: fixed; bottom: 50px; left: 10px; z-index:9999;">
        <!-- Recommendations Button -->
        <button onclick="toggleList()" style="padding:10px; font-size:14px; background:#007bff; color:white; border:none; cursor:pointer;">
            Show Recommendations
        </button>
        <div id="recommendations-box" style="display:none; background:white; padding:10px; border:1px solid black; max-height:250px; overflow:auto;">
            <h4>Recommended Spots</h4>
            <ul style="list-style-type: none; padding: 0;">{list_items}</ul>
        </div>
    </div>

    <!-- Chatbot UI -->
    <div style="position: fixed; bottom: 50px; right: 10px; z-index:9999;">
        <button onclick="toggleChat()" style="padding:10px; font-size:14px; background:#28a745; color:white; border:none; cursor:pointer;">
            Open Chatbot
        </button>
        <div id="chat-container" style="display:none; width:300px; height:400px; background:white; padding:10px; border:1px solid black; overflow:auto;">
            <h4>AI Chatbot</h4>
            <div id="chat-box" style="height:300px; overflow-y:auto; border-bottom:1px solid gray; padding:5px;"></div>
            <input type="text" id="user-input" placeholder="Type your message..." style="width:80%;" />
            <button onclick="sendChat()" style="width:18%; background:#007bff; color:white; border:none;">Send</button>
        </div>
    </div>

    <script>
        function toggleList() {{
            var listBox = document.getElementById("recommendations-box");
            listBox.style.display = (listBox.style.display === "none") ? "block" : "none";
        }}

        function toggleChat() {{
            var chatBox = document.getElementById("chat-container");
            chatBox.style.display = (chatBox.style.display === "none") ? "block" : "none";
        }}

        async function sendChat() {{
            let inputField = document.getElementById("user-input");
            let userText = inputField.value;
            if (!userText.trim()) return;

            let chatBox = document.getElementById("chat-box");
            chatBox.innerHTML += `<p><b>You:</b> ${'{'}userText{'}'}</p>`;

            inputField.value = ""; // Clear input field

            try {{
                let response = await fetch("http://127.0.0.1:5000/chatbot", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: JSON.stringify({{"query": userText}})
                }});
                let data = await response.json();
                chatBox.innerHTML += `<p><b>AI:</b> ${'{'}data.reply{'}'}</p>`;
                chatBox.scrollTop = chatBox.scrollHeight;
            }} catch (error) {{
                chatBox.innerHTML += `<p><b>AI:</b> Error fetching response.</p>`;
            }}
        }}
    </script>
    '''


    tourist_map.get_root().html.add_child(folium.Element(html))
    return tourist_map

recommendations = recommend_spots(user_location, radius, category_filter, season_filter, dataset)

# Generate Map with Chatbot & Recommendations
if recommendations.empty:
    print("No spots found. Try increasing the radius or changing the category.")
else:
    tourist_map = visualize_map_with_chatbot(user_location, recommendations)
    tourist_map.save("tourist_map_with_chatbot.html")
    print("Map saved as 'tourist_map_with_chatbot.html'")
