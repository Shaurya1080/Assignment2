import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
import openai

# Set up OpenAI client with the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example function to generate a response using GPT-4o
def get_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content']

# Test the function
print(get_openai_response("How do I set up a new source in Segment?"))


# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise Exception("OPENAI_API_KEY is not set in .env file.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Flask app setup
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"response": "Please ask a valid question."})

    # Generate response using OpenAI's GPT model
    try:
        response = client.Completions.create(
            model="gpt-4o",
            prompt=f"You are a helpful assistant for answering questions about Segment, mParticle, Lytics, and Zeotap.\nUser Question: {user_message}\nAssistant:",
            max_tokens=150,
            temperature=0.7,
        )
        bot_response = response.choices[0].text.strip()
    except Exception as e:
        bot_response = "Sorry, I couldn't process your request."

    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
