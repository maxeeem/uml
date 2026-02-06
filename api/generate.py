from flask import Flask, Blueprint, request, jsonify
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import zlib
import base64
import string
import os

# Load environment variables from .env file (for local development)
# Note: Vercel will use environment variables directly, so this won't interfere
load_dotenv()

# Create blueprint for the API
api_bp = Blueprint('api', __name__)

# Initialize OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Get the secret password from Vercel Environment Variables or .env file
# For localhost: set this to None or empty string to disable access code check
SECRET_ACCESS_CODE = os.environ.get("ACCESS_CODE")

# --- Schema for Structured Output (No Chatter) ---
class DiagramResponse(BaseModel):
    plantuml_code: str
    explanation: str

# --- Helper: PlantUML Encoder ---
def deflate_and_encode(plantuml_text):
    zlibbed_str = zlib.compress(plantuml_text.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4] # Strip zlib headers
    base64_bytes = base64.b64encode(compressed_string)
    base64_str = base64_bytes.decode('utf-8')
    plantuml_alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase + '-_'
    b64_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    trans_table = str.maketrans(b64_alphabet, plantuml_alphabet)
    return base64_str.translate(trans_table)

# Route handler - works for both Vercel (/) and local dev (/generate via blueprint)
def handle_request():
    try:
        data = request.json
        user_prompt = data.get('prompt', '')
        user_code = data.get('accessCode', '')

        # --- SECURITY CHECK ---
        # DISABLED FOR LOCALHOST: Only enforce access code if SECRET_ACCESS_CODE is set
        # When running locally, you can either:
        # 1. Not set ACCESS_CODE environment variable (it will be None)
        # 2. Or set ACCESS_CODE="" to explicitly disable it
        # For production (Vercel), set ACCESS_CODE to your secret password
        if SECRET_ACCESS_CODE and SECRET_ACCESS_CODE.strip():
            if user_code != SECRET_ACCESS_CODE:
                return jsonify({"error": "Incorrect Access Code."}), 403
        # ----------------------

        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Call OpenAI with Structured Outputs
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a PlantUML expert."},
                {"role": "user", "content": f"Create a diagram for: {user_prompt}"}
            ],
            response_format=DiagramResponse,
        )

        result = completion.choices[0].message.parsed
        
        # Encode URL
        encoded = deflate_and_encode(result.plantuml_code)
        url = f"http://www.plantuml.com/plantuml/svg/{encoded}"

        return jsonify({
            "url": url, 
            "plantuml_code": result.plantuml_code,
            "explanation": result.explanation
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route handler for rendering PlantUML code directly (without OpenAI)
def render_plantuml():
    try:
        data = request.json
        plantuml_code = data.get('plantuml_code', '')

        if not plantuml_code:
            return jsonify({"error": "No PlantUML code provided"}), 400

        # Encode URL
        encoded = deflate_and_encode(plantuml_code)
        url = f"http://www.plantuml.com/plantuml/svg/{encoded}"

        return jsonify({
            "url": url,
            "plantuml_code": plantuml_code
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# For Vercel: route at / (Vercel routes /api/generate and /api/render to this file)
app = Flask(__name__)

# Vercel routes both /api/generate and /api/render to this file
# We check the request data to determine which handler to use
@app.route('/', methods=['POST'])
def vercel_router():
    data = request.json or {}
    # If request has plantuml_code but no prompt, it's a render request
    if 'plantuml_code' in data and 'prompt' not in data:
        return render_plantuml()
    else:
        return handle_request()

# For local dev: register blueprint routes
api_bp.route('/generate', methods=['POST'])(handle_request)
api_bp.route('/render', methods=['POST'])(render_plantuml)

# For local testing (when run directly)
if __name__ == '__main__':
    app.run(debug=True, port=8000)
