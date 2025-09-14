import machine
import time

# pin 18 is the buzzer pin, which supports PWM
buzzer_pin = machine.PWM(machine.Pin(18))

freq = 440

for i in range(10):
    buzzer_pin.freq(int(freq))
    freq -= 50
    buzzer_pin.duty_u16(32768) # 50% duty cycle, 
    time.sleep_ms(100)
    buzzer_pin.duty_u16(0)
    time.sleep_ms(100)

