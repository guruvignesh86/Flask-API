from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
import random

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/otp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model (for future use)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# Twilio Credentials Model
class TwilioCredentials(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_sid = db.Column(db.String(255), nullable=False)
    auth_token = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)

# Function to get Twilio credentials
def get_twilio_credentials():
    with app.app_context():  # Ensure it's inside an app context
        creds = TwilioCredentials.query.first()
        if creds:
            return creds.account_sid, creds.auth_token, creds.phone_number
        return None, None, None

# Initialize database
with app.app_context():
    db.create_all()
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER = get_twilio_credentials()

# Initialize Twilio Client
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
else:
    print("❌ ERROR: Twilio credentials not found in the database")
    client = None

# Send OTP (without storing in DB)
@app.route("/send-otp", methods=["POST", "OPTIONS"])
@cross_origin()
def send_otp():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    
    data = request.json
    phone = data.get("phone")

    if not phone or not phone.startswith("+91"):
        return jsonify({"message": "Invalid Indian phone number"}), 400

    otp = str(random.randint(100000, 999999))

    try:
        if client:
            message = client.messages.create(
                body=f"Your OTP is {otp}",
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )
            return jsonify({"message": "OTP sent successfully!", "otp": otp})  # Send OTP in response (for testing)
        else:
            return jsonify({"message": "Twilio client not initialized"}), 500
    except Exception as e:
        return jsonify({"message": "Failed to send OTP", "error": str(e)}), 500

# OTP verification is now handled on the frontend

# CORS Preflight Response
def _build_cors_preflight_response():
    response = jsonify({})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    return response

# Run Flask app
if __name__ == "__main__":
    app.run(debug=True)
