# customer_support_bot.py
import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Load the environment variables from .env file
load_dotenv()
token = os.getenv("GITHUB_TOKEN")
if not token:
    raise Exception("GITHUB_TOKEN is not set in .env file.")

# Initialize the OpenAI client
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o"
client = OpenAI(base_url=endpoint, api_key=token)

# Sample product/business data
products = {
    "laptop": {
        "name": "X100 Pro Laptop",
        "price": "$1200",
        "availability": "In stock",
        "features": "16GB RAM, 1TB SSD, Intel i7 Processor"
    },
    "phone": {
        "name": "ZPhone Max",
        "price": "$799",
        "availability": "Limited stock",
        "features": "128GB storage, 12MP Camera, 5G enabled"
    }
}

def detect_tone(question):
    """
    Detect tone based on keywords in the question.
    Returns "empathetic", "urgent", or "helpful".
    """
    empathetic_keywords = ["broken", "problem", "issue", "not working", "delay"]
    urgent_keywords = ["urgent", "immediately", "asap", "help now", "fast", "quick"]
    if any(word in question.lower() for word in empathetic_keywords):
        return "empathetic"
    elif any(word in question.lower() for word in urgent_keywords):
        return "urgent"
    else:
        return "helpful"

def ask_customer_support(question, tone="helpful"):
    """
    Get a response from the GPT-4o model using a system message based on tone.
    If product-related keywords are detected, append product information.
    """
    system_message = "You are a helpful customer support assistant for an e-commerce store."
    if tone == "empathetic":
        system_message = "You are an empathetic customer support assistant. Be understanding and kind."
    elif tone == "urgent":
        system_message = "You are an urgent customer support assistant. Respond quickly and decisively."
    
    # Check if the question relates to any product and get product information
    product_response = ""
    for product_key, product_info in products.items():
        if re.search(rf'\b{product_key}\b', question.lower()):
            product_response = (
                f"Our {product_info['name']} is priced at {product_info['price']}. "
                f"Features: {product_info['features']}. "
                f"Availability: {product_info['availability']}."
            )
            break
    
    if product_response:
        question += "\n\n" + product_response
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ],
        temperature=0.7,
        max_tokens=500,
        model=model_name
    )
    return response.choices[0].message.content

# Initialize the Flask app
app = Flask(__name__, template_folder=str(Path(__file__).parent / "templates"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_bot_response():
    data = request.json
    user_message = data.get("message", "")
    tone = detect_tone(user_message)
    bot_response = ask_customer_support(user_message, tone)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
