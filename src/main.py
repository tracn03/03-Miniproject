from machine import Pin, ADC
import time

# Initialize ADC on GPIO28 (which is ADC channel 2)
photoresistor1 = ADC(Pin(28))
photoresistor2 = ADC(Pin(27))
buzzer_pin = machine.PWM(machine.Pin(18))

# Note mapping based on truth table: 00=silence, 01=C, 10=D, 11=E
note_mapping = {
    (False, False): (0, "silence"),
    (False, True): (262, "C"),   # 01 = C
    (True, False): (294, "D"),   # 10 = D  
    (True, True): (330, "E"),    # 11 = E
}

# Simple queue to store notes with durations
note_queue = []
current_note = None
current_note_start_time = 0
last_input_time = 0
silence_timeout = 5000  # 5 seconds in milliseconds

def add_note_to_queue(freq, duration_ms):
    """Add a note with duration to the queue"""
    if freq > 0:  # Only add non-silence notes
        note_queue.append((freq, duration_ms))
        print(f"Added note: {freq}Hz for {duration_ms}ms")

def play_queued_notes():
    """Play all notes in the queue"""
    print(f"Playing {len(note_queue)} notes from queue...")
    while note_queue:
        freq, duration_ms = note_queue.pop(0)
        print(f"Playing: {freq}Hz for {duration_ms}ms")
        
        buzzer_pin.freq(int(freq))
        buzzer_pin.duty_u16(32768)  # 50% duty cycle
        time.sleep(duration_ms / 1000)  # Convert ms to seconds
        buzzer_pin.duty_u16(0)  # Stop buzzer
        time.sleep(0.1)  # Small gap between notes

# Main loop
while True:
    # Read sensor values
    sensor1_raw = photoresistor1.read_u16()
    sensor2_raw = photoresistor2.read_u16()
    
    # Convert to boolean (True if light detected)
    sensor1 = sensor1_raw > 55000
    sensor2 = sensor2_raw > 55000
    
    current_time = time.ticks_ms()  # Current time in milliseconds
    sensor_state = (sensor1, sensor2)
    
    # Check if sensor state changed
    if current_note != sensor_state:
        # If we had a previous note, calculate its duration and add to queue
        if current_note is not None:
            duration = current_time - current_note_start_time
            if duration > 50:  # Only add notes longer than 50ms
                freq, note_name = note_mapping[current_note]
                add_note_to_queue(freq, duration)
        
        # Start tracking new note
        current_note = sensor_state
        current_note_start_time = current_time
        last_input_time = current_time
        
        # Play current note immediately
        freq, note_name = note_mapping[sensor_state]
        if freq > 0:
            buzzer_pin.freq(int(freq))
            buzzer_pin.duty_u16(32768)
            print(f"Playing: {note_name} ({freq}Hz)")
        else:
            buzzer_pin.duty_u16(0)
            print("Silence")
    
    # Update last input time if any sensor is active
    if sensor1 or sensor2:
        last_input_time = current_time
    
    # Check for silence timeout (5 seconds of no input)
    time_since_input = current_time - last_input_time
    if time_since_input >= silence_timeout and note_queue:
        # Stop current note
        buzzer_pin.duty_u16(0)
        current_note = None
        
        # Play all queued notes
        play_queued_notes()
        
        # Reset timing
        last_input_time = current_time
    
    time.sleep(0.05)  # Small delay for responsiveness
