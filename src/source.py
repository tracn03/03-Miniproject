import time
from typing import Dict, List, Optional, Tuple
from collections import deque


class NoteStore:
    
    def __init__(self, timeout_ms: int = 1000):
        self.timeout_ms = timeout_ms
        self.note_queue = deque()
        self.last_input_time = 0
        self.current_note = None
        self.current_note_start_time = 0
        
        self.note_mapping = {
            (False, False): (0, "silence"),
            (True, False): (262, "C4"),         
            (False, True): (294, "D4"),          
            (True, True): (330, "E4"),           
        }
    
    def add_sensor_input(self, sensor1_lit: bool, sensor2_lit: bool) -> Optional[Dict]:
        current_time = time.time() * 1000  
        sensor_state = (sensor1_lit, sensor2_lit)
        
        if self.current_note != sensor_state:
            if self.current_note is not None:
                duration = current_time - self.current_note_start_time
                if duration > 50:
                    note_info = self._get_note_info(self.current_note, duration)
                    self.note_queue.append(note_info)
                    print(f"Added note to queue: {note_info}")
            
            self.current_note = sensor_state
            self.current_note_start_time = current_time
            self.last_input_time = current_time
            
            return self._get_note_info(sensor_state, 0)
        
        if sensor1_lit or sensor2_lit:
            self.last_input_time = current_time
        
        return None
    
    def check_timeout(self) -> Optional[Dict]:
        if self.current_note is None:
            return None
            
        current_time = time.time() * 1000
        time_since_input = current_time - self.last_input_time
        
        if time_since_input >= self.timeout_ms:
            duration = current_time - self.current_note_start_time
            if duration > 50: 
                note_info = self._get_note_info(self.current_note, duration)
                self.note_queue.append(note_info)
                print(f"Timeout - added note to queue: {note_info}")

            self.current_note = None
            self.current_note_start_time = 0
            
            return self._get_note_info((False, False), 0)
        
        return None
    
    def pop_note(self) -> Optional[Dict]:
        if self.note_queue:
            note = self.note_queue.popleft()
            print(f"Popped note from queue: {note}")
            return note
        return None
    
    def clear_queue(self) -> None:
        self.note_queue.clear()
        print("Note queue cleared")
    
    def get_queue_status(self) -> Dict:
        return {
            "queue_size": len(self.note_queue),
            "current_note": self.current_note,
            "timeout_ms": self.timeout_ms,
            "last_input_time": self.last_input_time,
            "current_time": time.time() * 1000
        }
    
    def _get_note_info(self, sensor_state: Tuple[bool, bool], duration: float) -> Dict:
        frequency, note_name = self.note_mapping.get(sensor_state, (0, "unknown"))
        
        return {
            "frequency": frequency,
            "note_name": note_name,
            "duration_ms": int(duration),
            "sensor1_lit": sensor_state[0],
            "sensor2_lit": sensor_state[1],
            "timestamp": time.time() * 1000
        }


note_store = NoteStore()


def get_note_store() -> NoteStore:
    return note_store