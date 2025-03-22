from flask import Flask, jsonify, request
import RPi.GPIO as GPIO
import time

app = Flask(__name__)

# GPIO setup
SOLENOID_PIN = 26  # Change to your GPIO pin
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(SOLENOID_PIN, GPIO.OUT)

@app.route('/unlock', methods=['POST'])
def unlock_solenoid():
    try:
        data = request.get_json()  # Read incoming JSON data
        if data and data.get("auth") == "granted":
            print("Received unlock request. Activating solenoid lock...")
            GPIO.output(SOLENOID_PIN, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(SOLENOID_PIN, GPIO.LOW)
            print("Solenoid turned off after 3 seconds.")
            return jsonify({"message": "Solenoid unlocked for 3 seconds!"}), 200
        else:
            return jsonify({"error": "Invalid request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

