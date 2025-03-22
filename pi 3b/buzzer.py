import RPi.GPIO as GPIO
import time

# Define GPIO pins
TRIG = 23  # Ultrasonic sensor Trig pin
ECHO = 24  # Ultrasonic sensor Echo pin
RELAY_PIN = 17  # Relay module controlling the buzzer

# Threshold distance in cm
THRESHOLD_DISTANCE = 7
WAIT_TIME = 5  # 5-second delay before beeping

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.LOW)  # Ensure buzzer is OFF initially

def get_distance():
    """
    Measures the distance using HC-SR04 Ultrasonic Sensor.
    
    Returns:
        float: Distance in centimeters.
    """
    # Send 10Âµs pulse to trigger pin
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10Âµs pulse
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    # Record the last low timestamp for Echo pin
    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    # Record the last high timestamp for Echo pin
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    # Calculate pulse duration
    elapsed_time = stop_time - start_time

    # Convert duration to distance (Speed of sound: 34300 cm/s)
    distance = (elapsed_time * 34300) / 2  # Divide by 2 for round-trip

    return round(distance, 2)

try:
    print("Ultrasonic Sensor & Buzzer System Running...")
    while True:
        distance = get_distance()
        print(f"Distance: {distance} cm")

        if distance > THRESHOLD_DISTANCE:
            print("Object too far! Waiting 5 seconds before beeping...")
            start_time = time.time()

            # Wait for 5 seconds, but if the distance goes below threshold, stop waiting
            while time.time() - start_time < WAIT_TIME:
                distance = get_distance()
                if distance <= THRESHOLD_DISTANCE:
                    print("Object back within range. Cancelling beep.")
                    break  # Stop waiting and reset

            else:
                print("Buzzer Beeping!")
                while get_distance() > THRESHOLD_DISTANCE:
                    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Buzzer ON
                    time.sleep(0.3)  # Beep duration
                    GPIO.output(RELAY_PIN, GPIO.LOW)  # Buzzer OFF
                    time.sleep(0.3)  # Pause duration

        else:
            GPIO.output(RELAY_PIN, GPIO.LOW)  # Ensure buzzer is OFF
            print("Buzzer OFF! Object within range.")

        time.sleep(0.1)  # Small delay for stability

except KeyboardInterrupt:
    print("\nProcess interrupted by user.")
finally:
    GPIO.cleanup()  # Reset GPIO pins


