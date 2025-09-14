from machine import Pin, ADC
import time

# Initialize ADC on GPIO28 (which is ADC channel 2)
photoresistor1 = ADC(Pin(28))
photoresistor2 = ADC(Pin(27))
sensor1 = False
sensor2 = False
buzzer_pin = machine.PWM(machine.Pin(18))
freq = 440

note_mapping = {
    (False, False): (0, "silence"),
    (True, False): (400, "C"),
    (False, True): (500, "D"),
    (True, True): (600, "E"),
}

# Read the raw ADC value (0-65535 for 16-bit resolution)
while True:
    sensor1 = photoresistor1.read_u16()
    print(f"Sensor1: {sensor1}")
    sensor2 = photoresistor2.read_u16()
    print(f"Sensor2: {sensor2}")
    if sensor1 > 55000:
        sensor1 = True
    else:
        sensor1 = False
    if sensor2 > 55000:
        sensor2 = True
    else:
        sensor2 = False

    freq, note = note_mapping[(sensor1, sensor2)]
    
    if freq > 0:    
        buzzer_pin.freq(int(freq))
        buzzer_pin.duty_u16(32768) # 50% duty cycle
    else:
        buzzer_pin.duty_u16(0)
    time.sleep(0.25)
