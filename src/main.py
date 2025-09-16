from machine import Pin, ADC, PWM 
import time
import network 
import urequests as requests 
import ujson as json 

# WiFi setup function from internet
def connect_wifi():
    """Connect to WiFi using config file"""
    try:
        wifi_config = "config/wifi_config.json"
        with open(wifi_config, "r") as f:
            data = json.load(f)
        ssid = data["ssid"]
        passw = data["passw"]
        
        print(f"Connecting to WiFi {ssid}")
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        sta_if.connect(ssid, passw)
        
        # Wait for connection
        timeout = 10 
        while not sta_if.isconnected() and timeout > 0:
            print(f"Still trying to connect to {ssid}")
            time.sleep(1)
            timeout -= 1
            
        if sta_if.isconnected():
            print(f"Connected! IP: {sta_if.ifconfig()[0]}")
            return True
        else:
            print("Failed to connect to WiFi")
            return False
            
    except Exception as e:
        print(f"WiFi connection error: {e}")
        return False

# API configuration (edit to jasons branch for test)
API_BASE_URL = "https://raw.githubusercontent.com/tracn03/03-Miniproject/main/songs/starwars.json" 

# Initialize ADC on GPIO28 (which is ADC channel 2)
photoresistor1 = ADC(Pin(28))
photoresistor2 = ADC(Pin(27))
sensor1 = False
sensor2 = False
buzzer_pin = machine.PWM(machine.Pin(18))
freq = 440

# Song management
current_song = []
song_index = 0
last_fetch_time = 0
FETCH_INTERVAL = 30000  # Fetch new song every 30 seconds

def fetch_song_from_api():
    """Fetch song data from the server API"""
    try:
        print("Fetching song from API...")
        response = requests.get(f"{API_BASE_URL}")
        if response.status_code == 200:
            song_data = response.json()
            response.close() 
            return song_data.get("song", [])
        else:
            print(f"API error: {response.status_code}")
            response.close()
            return []
    except Exception as e:
        print(f"Failed to fetch song: {e}")
        return []

def play_song_note(note_data):
    """Play a single note from song data"""
    freq = note_data.get("freq", 0)
    duration = note_data.get("duration", 250)
    
    if freq > 0:
        buzzer_pin.freq(int(freq))
        buzzer_pin.duty_u16(32768)  # 50% duty cycle
        time.sleep(duration / 1000)  # Convert ms to seconds
        buzzer_pin.duty_u16(0)  # Turn off
    else:
        time.sleep(duration / 1000)  # Rest/silence

#sensor mode mapping
note_mapping = {
    (False, False): (0, "silence"),
    (True, False): (400, "C"),
    (False, True): (500, "D"),
    (True, True): (600, "E"),
}

wifi_connected = connect_wifi()

#modes of op
MODE_SENSOR = 0
MODE_API_SONG = 1
current_mode = MODE_SENSOR 

print("Pico Music System Started!")
if wifi_connected:
    print("WiFi connected - API song mode available")
    print("Cover both sensors for 2 seconds to switch modes")
else:
    print("No WiFi - sensor mode only")

# Add these variables for mode switching
mode_switch_start = 0
last_note_time = 0

while True:
    current_time = time.ticks_ms()
    
    # Read sensors
    sensor1_raw = photoresistor1.read_u16()
    sensor2_raw = photoresistor2.read_u16()
    
    sensor1 = sensor1_raw > 55000
    sensor2 = sensor2_raw > 55000
    
    # CHECK FOR MODE SWITCH
    if not sensor1 and not sensor2:  # Both sensors dark (covered)
        if mode_switch_start == 0:
            mode_switch_start = current_time
        elif current_time - mode_switch_start > 2000:  # 2 seconds
            # Switch modes
            current_mode = MODE_API_SONG if current_mode == MODE_SENSOR else MODE_SENSOR
            print(f"Switched to {'API Song' if current_mode == MODE_API_SONG else 'Sensor'} mode")
            mode_switch_start = 0
            song_index = 0  # Reset song position
    else:
        mode_switch_start = 0
    
    # Handle different modes
    if current_mode == MODE_SENSOR:
        freq, note = note_mapping[(sensor1, sensor2)]
        
        if freq > 0:    
            buzzer_pin.freq(int(freq))
            buzzer_pin.duty_u16(32768) # 50% duty cycle
        else:
            buzzer_pin.duty_u16(0)
        
        print(f"Sensor Mode - S1: {sensor1_raw}, S2: {sensor2_raw}, Note: {note}")
        time.sleep(0.25)
        
    elif current_mode == MODE_API_SONG:
        # API song mode
        # Fetch new song if needed
        if (current_time - last_fetch_time > FETCH_INTERVAL) or len(current_song) == 0:
            current_song = fetch_song_from_api()
            last_fetch_time = current_time
            song_index = 0
            print(f"Loaded song with {len(current_song)} notes")
        
        # Play song if we have one
        if len(current_song) > 0:
            if song_index < len(current_song):
                note_data = current_song[song_index]
                play_song_note(note_data)
                song_index += 1
                print(f"Playing note {song_index}/{len(current_song)}")
            else:
                # Song finished, restart
                song_index = 0
                print("Song finished, restarting...")
        else:
            print("No song available, waiting...")
            time.sleep(1)
