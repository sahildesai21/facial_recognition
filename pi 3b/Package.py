import network
import time
import urequests
import ubinascii
from machine import Pin

# Wi-Fi credentials
SSID = "Home_EXT"
PASSWORD = "habishyam0806"

# Twilio credentials
account_sid = "ACe9f0db72420b8793aaf335220f7845db"  # Twilio Account SID
auth_token = "43d1f95cca940b2dacf8f7257f393b29"   # Twilio Auth Token
twilio_number = "+12183288734"  # Twilio phone number
recipient_number = "+919686893760"  # Recipient phone number

# Ultrasonic sensor pins
TRIG_PIN = 13  # GPIO pin connected to the Trig pin of the sensor
ECHO_PIN = 12  # GPIO pin connected to the Echo pin of the sensor

# Variable to track whether the message has been sent
sms_sent = False

# Initialize the pins once
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Connect to Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Wi-Fi connected:", wlan.ifconfig())

# Function to URL encode the post data (as urllib is not available in MicroPython)
def urlencode(data):
    return '&'.join(f"{key}={value}" for key, value in data.items())

def send_sms(message_body):
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
        # Encode credentials in Base64
        credentials = account_sid + ":" + auth_token
        auth_header = "Basic " + ubinascii.b2a_base64(credentials.encode()).decode().strip()

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        # Prepare POST data
        post_data = {
            "To": recipient_number,
            "From": twilio_number,
            "Body": message_body
        }

        # URL-encode the data
        encoded_data = urlencode(post_data)

        print("Sending SMS...")
        print("POST Data:", encoded_data)  # Debug
        print("Headers:", headers)  # Debug

        # Send POST request to Twilio API
        response = urequests.post(url, data=encoded_data, headers=headers, timeout=10)
        
        print("Response Code:", response.status_code)
        print("Response Body:", response.text)

        if response.status_code == 201:
            print("SMS sent successfully!")
        else:
            print(f"Error sending SMS: {response.status_code} - {response.text}")
        
        response.close()

    except OSError as e:
        print("Network error during SMS:", e)

# Function to get distance from the ultrasonic sensor
def get_distance():
    # Trigger a pulse
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(10)
    trig.low()

    # Measure the time it takes for the echo to return
    pulse_duration = 0
    while echo.value() == 0:
        pulse_start = time.ticks_us()
    while echo.value() == 1:
        pulse_end = time.ticks_us()

    pulse_duration = time.ticks_diff(pulse_end, pulse_start)

    # Calculate distance in cm
    distance = (pulse_duration * 0.0343) / 2  # Speed of sound = 343 m/s or 0.0343 cm/us
    return distance

# Main program logic
def main():
    global sms_sent  # Declare the global variable to track SMS status
    connect_wifi()

    previous_distance = None  # Track the previous distance to detect threshold crossing

    while True:
        distance = get_distance()
        print("Distance:", distance, "cm")

        if distance < 17 and (previous_distance is None or previous_distance >= 17) and not sms_sent:
            send_sms("Package has been kept!!")
            sms_sent = True  # Set the flag to prevent further SMS until distance exceeds 17 cm
        
        elif distance >= 17 and (previous_distance is None or previous_distance < 17) and not sms_sent:
            send_sms("Locker is Empty!!")
            sms_sent = True  # Set the flag to prevent further SMS until distance falls below 17 cm

        # Reset the SMS flag if the distance has crossed the threshold in either direction
        if distance >= 17 or distance < 17:
            sms_sent = False

        # Update previous distance to check for threshold crossing
        previous_distance = distance

        time.sleep(2)  # Check every 2 seconds

# Run the main program
main()


