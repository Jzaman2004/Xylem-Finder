from flask import Flask, request, jsonify, send_from_directory
import os
from groq import Groq
from flask_cors import CORS
import json
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

# Replace with your actual API key
GROQ_API_KEY = "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"

# Mock database to store submitted missing person reports
missing_people_data = []

@app.route('/')
def home():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/api/get_missing_people', methods=['GET'])
def get_missing_people():
    global missing_people_data

    if len(missing_people_data) >= 5:
        return jsonify(missing_people_data[:5])

    client = Groq(api_key=GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "Generate at least 5 missing people from Bangladesh in JSON format with fields: "
                    "'name', 'date_missing', 'location', 'zip_code', 'confidence_percentage'. "
                    "No markdown, just plain JSON array."
                )},
                {"role": "user", "content": "Give me info about recent missing people in Bangladesh."}
            ]
        )

        content = response.choices[0].message.content.strip()

        # Try to parse the JSON output
        try:
            generated_people = json.loads(content)
        except Exception as e:
            print("JSON parsing error:", e)
            generated_people = []

        # Merge with user-submitted data
        combined = generated_people + missing_people_data
        return jsonify(combined[:5])

    except Exception as e:
        print("Error fetching from LLaMA:", e)
        return jsonify([])

@app.route('/api/report_missing_person', methods=['POST'])
def report_missing_person():
    data = request.json
    data['reported'] = True
    missing_people_data.insert(0, data)  # Insert at top
    return jsonify({"success": True})

@app.route('/api/generate_chart', methods=['GET'])
def generate_chart():
    global missing_people_data

    # Extract zip codes or coordinates
    locations = [person.get('zip_code') or person.get('coordinate') for person in missing_people_data]
    counts = {}
    for loc in locations:
        if loc:
            counts[loc] = counts.get(loc, 0) + 1

    if not counts:
        return jsonify({"chart": ""})

    # Generate bar chart
    plt.figure(figsize=(8, 4))
    plt.bar(counts.keys(), counts.values(), color='skyblue')
    plt.title('Missing People by Location')
    plt.xlabel('Location / Zip Code')
    plt.ylabel('Count')
    plt.xticks(rotation=45)

    # Convert to base64 image
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')

    return jsonify({"chart": f"data:image/png;base64,{img_base64}"})

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    client = Groq(api_key=GROQ_API_KEY)

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "You are an AI assistant helping users find information about missing people in Bangladesh."
                )},
                {"role": "user", "content": user_message}
            ]
        )
        ai_response = response.choices[0].message.content.strip()
        return jsonify({"reply": ai_response})
    except Exception as e:
        print("Chat API error:", e)
        return jsonify({"reply": "Sorry, I couldn't respond right now."})

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

if __name__ == '__main__':
    app.run(debug=True)