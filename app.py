from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import openai

# Load .env
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Set OPENAI_API_KEY in .env file")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__, template_folder="templates", static_folder="static")

# Role-based instructions
ROLE_PROMPTS = {
    "patient": "Use simple language, give self-care tips and safe advice.",
    "doctor": "Use clinical language, provide differential diagnosis and investigations.",
    "nurse": "Focus on triage, monitoring advice, and escalation instructions.",
    "pharmacist": "Focus on medication counseling, OTC options, and drug interactions."
}

MASTER_PROMPT = (
    "You are a safe, responsible Medical AI assistant. "
    "Never give unsafe prescriptions. Always advise to consult a doctor for serious symptoms. "
    "Answer based on the user role instructions."
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/message", methods=["POST"])
def message():
    data = request.get_json()
    user_msg = data.get("message", "")
    role = data.get("role", "patient")

    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    system_prompt = MASTER_PROMPT + "\nRole instruction: " + ROLE_PROMPTS.get(role, ROLE_PROMPTS["patient"])
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=400
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        reply_text = f"Error: {e}"

    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
