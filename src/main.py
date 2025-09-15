from machine import Pin, ADC
import time
from store import get_note_store

# Initialize ADC on GPIO28 (which is ADC channel 2)
photoresistor1 = ADC(Pin(28))
photoresistor2 = ADC(Pin(27))
sensor1 = False
sensor2 = False
buzzer_pin = machine.PWM(machine.Pin(18))
freq = 440

# Initialize the note store
note_store = get_note_store()

note_mapping = {
    (False, False): (0, "silence"),
    (True, False): (400, "C"),
    (False, True): (500, "D"),
    (True, True): (600, "E"),
}

# Read the raw ADC value (0-65535 for 16-bit resolution)
while True:
    # Read sensor values
    sensor1_raw = photoresistor1.read_u16()
    sensor2_raw = photoresistor2.read_u16()
    print(f"Sensor1: {sensor1_raw}, Sensor2: {sensor2_raw}")
    
    # Convert to boolean values
    sensor1_lit = sensor1_raw > 55000
    sensor2_lit = sensor2_raw > 55000
    
    # Add sensor input to note store
    current_note = note_store.add_sensor_input(sensor1_lit, sensor2_lit)
    
    # Check for timeout and handle playback
    timeout_note = note_store.check_timeout()
    
    # Determine which note to play
    note_to_play = current_note or timeout_note
    
    if note_to_play:
        freq = note_to_play["frequency"]
        note_name = note_to_play["note_name"]
        print(f"Playing: {note_name} ({freq}Hz)")
        
        if freq > 0:    
            buzzer_pin.freq(int(freq))
            buzzer_pin.duty_u16(32768) # 50% duty cycle
        else:
            buzzer_pin.duty_u16(0)
    
    # Check if we should start playback of stored notes
    if note_store.get_queue_status()["queue_size"] > 0 and not (sensor1_lit or sensor2_lit):
        # Check if enough time has passed since last input to start playback
        status = note_store.get_queue_status()
        time_since_input = status["current_time"] - status["last_input_time"]
        
        if time_since_input > 2000:  # 2 seconds of no input
            print("Starting playback of stored notes...")
            while note_store.get_queue_status()["queue_size"] > 0:
                stored_note = note_store.pop_note()
                if stored_note:
                    freq = stored_note["frequency"]
                    duration = stored_note["duration_ms"] / 1000.0  # Convert to seconds
                    note_name = stored_note["note_name"]
                    print(f"Playing stored note: {note_name} ({freq}Hz) for {duration:.2f}s")
                    
                    if freq > 0:
                        buzzer_pin.freq(int(freq))
                        buzzer_pin.duty_u16(32768)
                        time.sleep(duration)
                    else:
                        buzzer_pin.duty_u16(0)
                        time.sleep(duration)
            
            print("Playback complete!")
    
    time.sleep(0.25)
