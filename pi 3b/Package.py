import RPi.GPIO as GPIO
import time
import requests
import base64

# Wi-Fi is managed by the OS in Raspberry Pi, so no `network` module is needed.

# Twilio credentials
account_sid = "ACef0891eedfcf4aa3bbc75430a3e930fe"  # Twilio Account SID
auth_token = "f7b3d04842540d2f8d5acf447ca9bc01"     # Twilio Auth Token
twilio_number = "+19034595120"  # Twilio phone number
recipient_number = "+919108211783"  # Recipient phone number

# Define GPIO pins
TRIG_PIN = 27
ECHO_PIN = 22 

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

# SMS flag
sms_sent = False

# Function to send SMS via Twilio
def send_sms(message_body):
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        # Create Basic Auth header
        credentials = f"{account_sid}:{auth_token}"
        auth_header = "Basic " + base64.b64encode(credentials.encode()).decode()

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        post_data = {
            "To": recipient_number,
            "From": twilio_number,
            "Body": message_body
        }

        # Send POST request
        response = requests.post(url, data=post_data, headers=headers, timeout=10)
        
        if response.status_code == 201:
            print("? SMS sent successfully!")
        else:
            print(f"? Error sending SMS: {response.status_code} - {response.text}")

    except requests.RequestException as e:
        print("? Network error during SMS:", e)

# Function to measure distance using HC-SR04
def get_distance():
    GPIO.output(TRIG_PIN, False)
    time.sleep(0.1)  # Short delay

    GPIO.output(TRIG_PIN, True)
    time.sleep(0.00001)  # Send 10us pulse
    GPIO.output(TRIG_PIN, False)

    start_time = time.time()
    stop_time = time.time()

    # Wait for echo to go high
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    # Wait for echo to go low
    while GPIO.input(ECHO_PIN) == 1:
        stop_time = time.time()

    # Calculate time difference
    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Convert to cm

    return round(distance, 2)

# Main function
def main():
    global sms_sent
    previous_distance = None  

    try:
        while True:
            distance = get_distance()
            print(f"?? Distance: {distance} cm")

            if distance < 17 and (previous_distance is None or previous_distance >= 17) and not sms_sent:
                send_sms("?? Package has been kept!!")
                sms_sent = True  

            elif distance >= 17 and (previous_distance is None or previous_distance < 17) and not sms_sent:
                send_sms("?? Locker is Empty!!")
                sms_sent = True  

            # Reset SMS flag when distance changes
            if (previous_distance is not None) and (distance >= 17 or distance < 17):
                sms_sent = False

            previous_distance = distance

            time.sleep(2)  # Delay to prevent excessive SMS sending

    except KeyboardInterrupt:
        print("\nExiting...")

    finally:
        GPIO.cleanup()  # Reset GPIO settings

# Run the main function
if __name__ == "__main__":
    main()


