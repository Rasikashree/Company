from flask import Flask, request, jsonify, send_file, send_from_directory
import firebase_admin
from firebase_admin import credentials, db
import os

app = Flask(__name__)

# Initialize Firebase Admin SDK with your service account key
cred = credentials.Certificate("credentials.json")  # Ensure this JSON file is in the same directory
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://skyspheretech-822be-default-rtdb.firebaseio.com'  # Corrected Firebase database URL
})

# Reference to the messages collection in Firebase
messages_ref = db.reference("messages")

def insert_message(data):
    """
    Inserts a message into the Firebase Realtime Database.
    """
    messages_ref.push(data)  # Pushes new data as a unique entry

@app.route('/')
def index():
    return send_file('index.html')  # Serve the form page directly

# Route to serve static files (images, CSS, JS) from the same directory
@app.route('/<path:filename>')
def serve_file(filename):
    """
    Serve static files (images, CSS, JS) from the current directory.
    """
    return send_from_directory(os.getcwd(), filename)

@app.route('/send-message', methods=['POST'])
def send_message():
    # Check if JSON data is present in the request
    if not request.is_json:
        return jsonify({"error": "Invalid data format; expected JSON"}), 400

    # Parse the JSON data
    data = request.get_json()
    
    # Log received data
    print("Received data:", data)

    # Check for required fields
    required_fields = ['name', 'email', 'phone', 'project', 'subject', 'message']
    missing_fields = [field for field in required_fields if field not in data]

    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400

    try:
        # Insert data into Firebase
        insert_message(data)
        print("Message inserted into Firebase:", data)

        return jsonify({"status": "success", "message": "Data received and stored successfully"}), 200

    except Exception as e:
        print("Error inserting data:", e)
        return jsonify({"error": "Failed to store data"}), 500

# Test Firebase connection on app start
try:
    test_ref = db.reference('test')
    test_ref.set({'test_key': 'test_value'})  # Sample data to test the connection
    print("Firebase connection successful.")
except Exception as e:
    print("Error connecting to Firebase:", e)

# Error handling for 404 errors
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({"error": "Resource not found"}), 404

# Error handling for 500 errors
@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
