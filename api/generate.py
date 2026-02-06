from flask import Flask, Blueprint, request, jsonify
from openai import OpenAI
from pydantic import BaseModel, ValidationError
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
                return jsonify({"error": "Incorrect Access Code. Please check your access code and try again."}), 403
        # ----------------------

        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Call OpenAI with Structured Outputs
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a PlantUML expert. Always return valid PlantUML syntax. Start your PlantUML code with @startuml and end with @enduml."},
                    {"role": "user", "content": f"Create a diagram for: {user_prompt}"}
                ],
                response_format=DiagramResponse,
            )

            # Check if parsing was successful
            if not completion.choices or not completion.choices[0].message.parsed:
                return jsonify({
                    "error": "AI did not generate a valid response. Please try again."
                }), 500

            result = completion.choices[0].message.parsed
            
            # Validate that we got valid PlantUML code
            if not result.plantuml_code or not result.plantuml_code.strip():
                return jsonify({"error": "AI did not generate valid PlantUML code. Please try again."}), 500
            
            # Encode URL
            encoded = deflate_and_encode(result.plantuml_code)
            url = f"http://www.plantuml.com/plantuml/svg/{encoded}"

            return jsonify({
                "url": url, 
                "plantuml_code": result.plantuml_code,
                "explanation": result.explanation
            })
        except ValidationError as validation_error:
            # Handle Pydantic validation errors (when OpenAI response doesn't match schema)
            return jsonify({
                "error": "AI generated invalid PlantUML code that doesn't match the expected format. Please try rephrasing your request or try again."
            }), 500
        except Exception as openai_error:
            # Handle OpenAI-specific errors more gracefully
            error_msg = str(openai_error)
            error_type = type(openai_error).__name__
            
            # Check for validation/pattern matching errors in multiple ways
            if ("did not match the expected pattern" in error_msg or 
                "validation" in error_msg.lower() or
                "pattern" in error_msg.lower() or
                "ValidationError" in error_type or
                "InvalidResponseFormat" in error_type):
                return jsonify({
                    "error": "AI generated invalid PlantUML code. Please try rephrasing your request or try again."
                }), 500
            elif "rate limit" in error_msg.lower():
                return jsonify({
                    "error": "OpenAI API rate limit exceeded. Please wait a moment and try again."
                }), 429
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                return jsonify({
                    "error": "OpenAI API authentication failed. Please check your API key configuration."
                }), 500
            else:
                # Return a more user-friendly message, but include error type for debugging
                return jsonify({
                    "error": f"AI generation failed. Please try again. (Error: {error_type})"
                }), 500

    except Exception as e:
        # Handle other errors (like access code, missing prompt, etc.)
        error_msg = str(e)
        return jsonify({"error": error_msg}), 500

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

# Handle GET requests (shouldn't happen for API routes, but just in case)
@app.route('/', methods=['GET'])
def get_handler():
    return jsonify({"error": "Method not allowed. Use POST."}), 405

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
