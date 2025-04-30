from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import pandas as pd
from geopy.distance import geodesic

# Load dataset
data = pd.read_csv("indianspots.csv")
dataset = pd.DataFrame(data)

# Configure Gemini API
API_KEY = "AIzaSyDmYmUXtC0KvrIU6PqNMyyJutIzqDcAd1c"  
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")
    
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

def compute_distances(df, user_location):
    df = df.copy() 
    df["Distance"] = df.apply(
        lambda row: geodesic(user_location, (row["Latitude"], row["Longitude"])).km, axis=1
    )
    return df

def ai_chatbot_response(user_query, recommendations):
    try:
        recommendation_text = "\n".join(
            [
                f"{row['Name']} ({row['Categories']}), Best Season: {row['Season']}, Rating: {row['Rating']}, Distance: {row['Distance']:.2f} km"
                for _, row in recommendations.iterrows()
            ]
        )

        prompt = f"""
        You are an AI assistant for a tourism recommendation system. Your task is to answer user queries using the provided tourist spot recommendations.

        Available recommendations:
        {recommendation_text}

        User Query: "{user_query}"

        Provide a helpful and relevant response.
        """
        
        print("\n====== DEBUGGING LOGS ======")
        print(f"User Query: {user_query}")
        print(f"Generated Prompt:\n{prompt}")

        
        response = model.generate_content(prompt)
        
        
        if not response:
            print("AI Response is None.")
            return "Error: No response received from AI."

        
        if not hasattr(response, "text"):
            print(f"AI Response Missing 'text' Attribute. Raw Response: {response}")
            return f"Error: AI Response format incorrect. Raw response: {response}"

        print(f"AI Response: {response.text}") 
        return response.text

    except Exception as e:
        print(f"AI Processing Error: {e}")
        return f"Error: {str(e)}"


@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_query = request.json.get("query", "")
    
    if not user_query:
        return jsonify({"reply": "Please enter a valid question."})

    try:
        user_location = (12.971318, 79.163892)  
        dataset_with_distance = compute_distances(dataset, user_location)

        recommendations = dataset_with_distance.sort_values(by="Distance").head(20)
        ai_response = ai_chatbot_response(user_query, recommendations)

        return jsonify({"reply": ai_response})

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"reply": "Sorry, an error occurred on the server."})
    
if __name__ == '__main__':
    app.run(debug=True)
