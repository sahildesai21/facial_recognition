from machine import Pin, time_pulse_us
import time

# Define GPIO pins
TRIG_PIN = 4  # New Trig pin
ECHO_PIN = 8  # New Echo pin
RELAY_PIN = 9  # New Relay pin

# Set up pins
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
relay = Pin(RELAY_PIN, Pin.OUT)

# Function to measure distance
def get_distance():
    # Send a 10us pulse to trigger
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # Measure the pulse width on the echo pin
    pulse_time = time_pulse_us(echo, 1, 30000)  # Timeout after 30ms
    if pulse_time == -1:
        # No echo received, return a large invalid distance
        return -1

    # Convert pulse duration to distance in cm
    distance = (pulse_time / 2) / 29.1  # Speed of sound is ~343 m/s
    return distance

# Variables for tracking door state
door_open = False
door_open_time = 0

try:
    while True:
        distance = get_distance()
        current_time = time.ticks_ms()

        if distance == -1:
            print("No echo received. Check sensor and connections.")
        else:
            print("Distance: {:.2f} cm".format(distance))

        if distance != -1 and distance <= 10:
            relay.value(0)  # Deactivate relay (door closed, buzzer off)
            door_open = False  # Reset door state
        else:
            if not door_open:
                door_open = True
                door_open_time = current_time  # Record the time the door was opened

            if time.ticks_diff(current_time, door_open_time) >= 7000:  # 7 seconds
                # Make the buzzer beep
                relay.value(1)
                time.sleep(0.3)  # Buzzer on for 200ms
                relay.value(0)
                time.sleep(0.7)  # Buzzer off for 300ms

        time.sleep(0.1)  # Small delay to stabilize readings

except KeyboardInterrupt:
    print("Program stopped")
    relay.value(0)  # Ensure relay is off
