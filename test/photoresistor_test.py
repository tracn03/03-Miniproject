from machine import Pin, ADC
import time

# Initialize ADC on GPIO28 (which is ADC channel 2)
adc = ADC(Pin(28))
buzzer_pin = machine.PWM(machine.Pin(18))
freq = 440



# Read the raw ADC value (0-65535 for 16-bit resolution)
while True:
    adc_value = adc.read_u16()
    
    # Convert to voltage (3.3V reference)
    voltage = (adc_value / 65535) * 3.3
    if (adc_value>60000):
        buzzer_pin.freq(int(freq))
        buzzer_pin.duty_u16(32768) # 50% duty cycle
    else:
        buzzer_pin.duty_u16(0)
    print(f"Raw ADC: {adc_value}, Voltage: {voltage:.3f}V")
    time.sleep(0.5)