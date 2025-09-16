from machine import Pin, PWM
import time

class TwinkleStarSound:
    def __init__(self, pin=15):
        self.buzzer = PWM(Pin(pin))
        self.buzzer.duty_u16(0)
        self.notes = {
            "C4": 262, "D4": 294, "E4": 330, "F4": 349,
            "G4": 392, "A4": 440, "B4": 494, "C5": 523,
            "D5": 587, "E5": 659, "F5": 698, "G5": 784,
            "REST": 0
        }

        # premade melody
        self.twinkle = [
            ("C4",0.5),("C4",0.5),("G4",0.5),("G4",0.5),
            ("A4",0.5),("A4",0.5),("G4",1.0),
            ("F4",0.5),("F4",0.5),("E4",0.5),("E4",0.5),
            ("D4",0.5),("D4",0.5),("C4",1.0),

            ("G4",0.5),("G4",0.5),("F4",0.5),("F4",0.5),
            ("E4",0.5),("E4",0.5),("D4",1.0),
            ("G4",0.5),("G4",0.5),("F4",0.5),("F4",0.5),
            ("E4",0.5),("E4",0.5),("D4",1.0),

            ("C4",0.5),("C4",0.5),("G4",0.5),("G4",0.5),
            ("A4",0.5),("A4",0.5),("G4",1.0),
            ("F4",0.5),("F4",0.5),("E4",0.5),("E4",0.5),
            ("D4",0.5),("D4",0.5),("C4",1.0)
        ]

    def play(self, note, duration=0.5):
        if note == "REST":
            self.buzzer.duty_u16(0)
        else:
            self.buzzer.freq(self.notes[note])
            self.buzzer.duty_u16(30000)  # volume
        time.sleep(duration)
        self.buzzer.duty_u16(0)
        time.sleep(0.05)

    def play_twinkle(self):
        for note, duration in self.twinkle:
            self.play(note, duration)
