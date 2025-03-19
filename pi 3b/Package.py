import network
import time
import urequests
import ubinascii
from machine import Pin


SSID = "Home_5G_EXT"
PASSWORD = "habishyam0806"

# Twilio credentials
account_sid = "ACef0891eedfcf4aa3bbc75430a3e930fe"  # Twilio Account SID
auth_token = "22cd5446198f3ad2920b85c34ebc248b"   # Twilio Auth Token
twilio_number = "+19034595120"  # Twilio phone number
recipient_number = "+919686893760"  # Recipient phone number


TRIG_PIN = 13  
ECHO_PIN = 12  


sms_sent = False


trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Connecting to Wi-Fi...")
    while not wlan.isconnected():
        time.sleep(1)
    print("Wi-Fi connected:", wlan.ifconfig())


def urlencode(data):
    return '&'.join(f"{key}={value}" for key, value in data.items())

def send_sms(message_body):
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        
      
        credentials = account_sid + ":" + auth_token
        auth_header = "Basic " + ubinascii.b2a_base64(credentials.encode()).decode().strip()

        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/x-www-form-urlencoded"
        }

   
        post_data = {
            "To": recipient_number,
            "From": twilio_number,
            "Body": message_body
        }


        encoded_data = urlencode(post_data)

        print("Sending SMS...")
        print("POST Data:", encoded_data)  
        print("Headers:", headers)  

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


def get_distance():
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
    distance = (pulse_duration * 0.0343) / 2  
    return distance


def main():
    global sms_sent  
    connect_wifi()

    previous_distance = None  

    while True:
        distance = get_distance()
        print("Distance:", distance, "cm")

        if distance < 17 and (previous_distance is None or previous_distance >= 17) and not sms_sent:
            send_sms("Package has been kept!!")
            sms_sent = True  # Set the flag to prevent further SMS until distance exceeds 17 cm
        
        elif distance >= 17 and (previous_distance is None or previous_distance < 17) and not sms_sent:
            send_sms("Locker is Empty!!")
            sms_sent = True  # Set the flag to prevent further SMS until distance falls below 17 cm

        
        if distance >= 17 or distance < 17:
            sms_sent = False

        
        previous_distance = distance

        time.sleep(2)  


main()





