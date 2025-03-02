
from flask import Flask, request, jsonify
from flask_cors import CORS
from llama_cpp import Llama
import os


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/", methods=["GET"])
def home():
    return "Welcome to the AI Chatbot API! Use the /chat endpoint to interact."
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Return an empty response with HTTP 204 (No Content)


# Load the local LLM model
MODEL_PATH = "model.gguf"  # Ensure this file exists in the directory
llm = Llama(model_path=MODEL_PATH)

# Store chat history for each session
chat_history = []

chat_history = []

def generate_response(prompt):
    """Generate AI response using Llama model."""
    
    # Combine chat history with the new prompt
    chat_history.append({"role": "user", "content": prompt})
    full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    full_prompt += f"\nUser: {prompt}\nAssistant: "

    try:
        # Generate response from the LLM
        response = llm(full_prompt, max_tokens=512, stop=["\n"])
        
        # Extract response text safely
        if isinstance(response, dict) and "choices" in response:
            assistant_reply = response["choices"][0]["text"].strip()
        else:
            assistant_reply = "⚠️ Error: Unexpected response format from LLM."

    except Exception as e:
        assistant_reply = f"⚠️ Error generating response: {str(e)}"

    # Store in chat history
    chat_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply



def generate_response(prompt):
    chat_history.append({"role": "user", "content": prompt})
    
    response = llm(chat_history, max_tokens=512, stop=["\n"])
    
    chat_history.append({"role": "assistant", "content": response["choices"][0]["text"]})
    return response["choices"][0]["text"]
chat_history = []

def generate_response(prompt):
    """Generate AI response using Mistral-7B with chat history."""
    
    # Combine chat history with the new prompt
    full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
    full_prompt += f"\nUser: {prompt}\nAssistant: "

    # Generate response from the LLM
    response = llm(full_prompt, max_tokens=512, stop=["\n"])

    # Extract the response text safely
    if isinstance(response, dict) and "choices" in response:
        assistant_reply = response["choices"][0]["text"].strip()
    else:
        assistant_reply = "⚠️ Error: Unexpected response format from LLM."

    # Store in chat history
    chat_history.append({"role": "user", "content": prompt})
    chat_history.append({"role": "assistant", "content": assistant_reply})

    return assistant_reply



def moderate_content(user_input):
    """Check for inappropriate content before responding"""
    flagged_words = ["hate", "violence", "racism"]
    for word in flagged_words:
        if word in user_input.lower():
            return "⚠️ Content flagged. Please rephrase your message."

    return generate_response(user_input)

@app.route("/chat", methods=["POST"])
def chat():
    """Handle user chat input and generate response"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400

        user_input = data["message"]
        response = moderate_content(user_input)
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
