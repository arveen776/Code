import numpy as np
import sounddevice as sd
import time
from collections import deque
import threading
import cv2
import webbrowser

class KnockDetector:
    def __init__(self):
        # Audio settings
        self.sample_rate = 44100  # Hz
        self.channels = 1
        self.chunk_size = 1024
        
        # Knock detection settings (calibrated for your microphone)
        self.threshold = 0.0001  # Knock detection threshold - based on your mic test
        self.knock_cooldown = 0.15  # Minimum time between knocks (seconds)
        self.pattern_timeout = 3.0  # Max time to complete a knock pattern (seconds)
        
        # Pattern storage
        self.current_pattern = []
        self.last_knock_time = 0
        self.pattern_start_time = 0
        
        # Known patterns (intervals between knocks in seconds)
        self.patterns = {
            'shave_and_haircut': {
                'pattern': [0.3, 0.3, 0.6, 0.3, 0.8],  # Classic "shave and a haircut" knock
                'tolerance': 0.15,
                'action': '💈 Shave and a Haircut - Opening Browser',
                'description': 'Knock-Knock-Knock... Knock... Knock'
            },
            'quick_double': {
                'pattern': [0.2, 0.2],  # Two quick knocks
                'tolerance': 0.1,
                'action': '⚡ Quick Double - Play/Pause',
                'description': 'Knock-Knock (fast)'
            },
            'triple': {
                'pattern': [0.3, 0.3, 0.3],  # Three evenly spaced knocks
                'tolerance': 0.15,
                'action': '🤖 Triple Knock - Open ChatGPT',
                'description': 'Knock-Knock-Knock (even)'
            },
            'secret_code': {
                'pattern': [0.3, 0.6, 0.3, 0.6],  # Short-Long-Short-Long
                'tolerance': 0.15,
                'action': '🔐 Secret Code - Unlock Feature',
                'description': 'Knock... Knock... (alternating)'
            },
            'emergency': {
                'pattern': [0.2, 0.2, 0.2, 0.2, 0.2],  # Five rapid knocks
                'tolerance': 0.1,
                'action': '🚨 Emergency - Alert Mode',
                'description': 'Knock-Knock-Knock-Knock-Knock (rapid)'
            }
        }
        
        # Recording mode
        self.recording_mode = False
        self.recorded_pattern = []
        
        # Running flag
        self.running = False
        
        # Audio buffer for visualization
        self.audio_buffer = deque(maxlen=200)
        self.peak_buffer = deque(maxlen=50)
        
        # For detecting sudden volume changes (knocks are sharp/transient)
        self.previous_volume = 0
        self.spike_threshold = 0.01  # Minimum volume increase to count as knock (calibrated for your mic)
        
        # Visual window
        self.window_width = 800
        self.window_height = 600
        self.knock_flash_time = 0
        self.last_matched_pattern = None
        self.last_match_time = 0
        self.current_spike = 0  # For display
        
    def calculate_intervals(self, knock_times):
        """Calculate intervals between knocks"""
        if len(knock_times) < 2:
            return []
        intervals = []
        for i in range(1, len(knock_times)):
            intervals.append(knock_times[i] - knock_times[i-1])
        return intervals
    
    def match_pattern(self, intervals):
        """Check if intervals match any known pattern"""
        best_match = None
        best_score = float('inf')
        
        for pattern_name, pattern_data in self.patterns.items():
            expected = pattern_data['pattern']
            tolerance = pattern_data['tolerance']
            
            # Check if number of intervals match
            if len(intervals) != len(expected):
                continue
            
            # Calculate how well the pattern matches
            differences = []
            for i in range(len(intervals)):
                diff = abs(intervals[i] - expected[i])
                differences.append(diff)
            
            # Check if all differences are within tolerance
            if all(d <= tolerance for d in differences):
                avg_diff = sum(differences) / len(differences)
                if avg_diff < best_score:
                    best_score = avg_diff
                    best_match = pattern_name
        
        return best_match
    
    def perform_action(self, pattern_name):
        """Perform action based on matched pattern"""
        if pattern_name in self.patterns:
            action = self.patterns[pattern_name]['action']
            print(f"\n🎯 PATTERN MATCHED: {pattern_name.upper()}")
            print(f"   Action: {action}")
            print("-" * 50)
            
            # Store for visual display
            self.last_matched_pattern = pattern_name
            self.last_match_time = time.time()
            
            # Perform actual actions based on pattern
            if pattern_name == 'triple':
                # Open ChatGPT
                print("   Opening ChatGPT.com in browser...")
                webbrowser.open('https://chatgpt.com')
            
            # Add more actions here:
            # elif pattern_name == 'quick_double':
            #     # Example: Play/Pause
            #     import keyboard
            #     keyboard.press_and_release('space')
            # elif pattern_name == 'shave_and_haircut':
            #     # Example: Open another website
            #     webbrowser.open('https://www.google.com')
            # etc.
            
            return action
        return None
    
    def draw_visual_window(self):
        """Create visual window showing knock detection"""
        # Create blank canvas
        canvas = np.zeros((self.window_height, self.window_width, 3), dtype=np.uint8)
        canvas[:] = (20, 20, 20)  # Dark background
        
        # Title
        cv2.putText(canvas, "SECRET KNOCK DETECTOR", (20, 40), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2)
        
        # Draw audio waveform
        if len(self.audio_buffer) > 0:
            wave_y_start = 100
            wave_height = 150
            wave_center = wave_y_start + wave_height // 2
            
            # Draw waveform background
            cv2.rectangle(canvas, (20, wave_y_start), 
                         (self.window_width - 20, wave_y_start + wave_height), 
                         (40, 40, 40), -1)
            
            # Draw threshold line
            threshold_y = int(wave_center - (self.threshold * wave_height / 2))
            cv2.line(canvas, (20, threshold_y), 
                    (self.window_width - 20, threshold_y), (0, 0, 255), 2)
            cv2.putText(canvas, f"Threshold: {self.threshold:.2f}", 
                       (self.window_width - 180, threshold_y - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            
            # Draw waveform
            buffer_list = list(self.audio_buffer)
            points = []
            for i, volume in enumerate(buffer_list):
                x = int(20 + (i / len(buffer_list)) * (self.window_width - 40))
                y = int(wave_center - (volume * wave_height / 2))
                y = max(wave_y_start, min(wave_y_start + wave_height, y))
                points.append((x, y))
            
            # Draw the waveform line
            if len(points) > 1:
                for i in range(len(points) - 1):
                    color = (0, 255, 0) if buffer_list[i] < self.threshold else (0, 255, 255)
                    cv2.line(canvas, points[i], points[i + 1], color, 2)
            
            # Current volume indicator
            current_vol = buffer_list[-1] if buffer_list else 0
            cv2.putText(canvas, f"Volume: {current_vol:.3f}", 
                       (30, wave_y_start - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            # Spike indicator
            spike_color = (0, 255, 0) if self.current_spike > self.spike_threshold else (100, 100, 100)
            cv2.putText(canvas, f"Spike: {self.current_spike:.3f}", 
                       (200, wave_y_start - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, spike_color, 1)
            
            # Detection status
            vol_ok = current_vol > self.threshold
            spike_ok = self.current_spike > self.spike_threshold
            status_text = "✓ Volume OK" if vol_ok else "✗ Volume Low"
            status_color = (0, 255, 0) if vol_ok else (100, 100, 100)
            cv2.putText(canvas, status_text, 
                       (400, wave_y_start - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 1)
            
            status_text2 = "✓ Spike OK" if spike_ok else "✗ Spike Low"
            status_color2 = (0, 255, 0) if spike_ok else (100, 100, 100)
            cv2.putText(canvas, status_text2, 
                       (580, wave_y_start - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color2, 1)
        
        # Knock flash indicator
        knock_y = 280
        if time.time() - self.knock_flash_time < 0.3:
            cv2.circle(canvas, (self.window_width // 2, knock_y), 50, (0, 255, 255), -1)
            cv2.putText(canvas, "KNOCK!", (self.window_width // 2 - 60, knock_y + 10),
                       cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 2)
        else:
            cv2.circle(canvas, (self.window_width // 2, knock_y), 50, (60, 60, 60), 2)
        
        # Current pattern display
        pattern_y = 370
        cv2.putText(canvas, f"Current Pattern: {len(self.current_pattern)} knock(s)", 
                   (30, pattern_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Draw knock indicators
        if self.current_pattern:
            for i in range(min(len(self.current_pattern), 10)):
                x = 50 + i * 70
                cv2.circle(canvas, (x, pattern_y + 40), 20, (0, 255, 0), -1)
                cv2.putText(canvas, str(i + 1), (x - 8, pattern_y + 48),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
            
            # Show intervals
            if len(self.current_pattern) >= 2:
                intervals = self.calculate_intervals(self.current_pattern)
                interval_text = " -> ".join([f"{i:.2f}s" for i in intervals])
                cv2.putText(canvas, f"Intervals: {interval_text}", 
                           (30, pattern_y + 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Pattern matching result
        match_y = 480
        if self.last_matched_pattern and time.time() - self.last_match_time < 3.0:
            # Success banner
            cv2.rectangle(canvas, (20, match_y - 10), 
                         (self.window_width - 20, match_y + 60), 
                         (0, 200, 0), -1)
            cv2.putText(canvas, f"MATCHED: {self.last_matched_pattern.upper()}", 
                       (40, match_y + 20),
                       cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2)
            action = self.patterns[self.last_matched_pattern]['action']
            cv2.putText(canvas, action, 
                       (40, match_y + 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)
        
        # Known patterns list
        list_y = 550
        cv2.putText(canvas, "Known Patterns:", 
                   (30, list_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (150, 150, 150), 1)
        
        pattern_names = list(self.patterns.keys())[:5]
        patterns_text = ", ".join([p.replace('_', ' ').title() for p in pattern_names])
        cv2.putText(canvas, patterns_text, 
                   (30, list_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Settings display
        settings_y = self.window_height - 40
        cv2.putText(canvas, f"Settings: Vol Threshold={self.threshold:.2f} | Spike Threshold={self.spike_threshold:.2f}", 
                   (20, settings_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
        
        # Instructions
        cv2.putText(canvas, "Press 'q' to quit | Knock on your desk to detect patterns", 
                   (20, self.window_height - 15),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 100, 100), 1)
        
        return canvas
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            print(f"Audio Status: {status}")
        
        # Calculate volume (RMS)
        volume = np.sqrt(np.mean(indata**2))
        self.audio_buffer.append(volume)
        
        current_time = time.time()
        
        # Detect knock (sudden spike in volume - characteristic of impacts)
        volume_spike = volume - self.previous_volume
        self.previous_volume = volume
        self.current_spike = volume_spike  # Store for display
        
        # A knock is: loud enough AND a sudden increase (spike)
        is_knock = (volume > self.threshold) and (volume_spike > self.spike_threshold)
        
        if is_knock:
            # Check cooldown to avoid detecting same knock multiple times
            if current_time - self.last_knock_time > self.knock_cooldown:
                self.last_knock_time = current_time
                self.knock_flash_time = current_time  # For visual flash
                
                # Start new pattern if timeout exceeded
                if not self.current_pattern or current_time - self.pattern_start_time > self.pattern_timeout:
                    self.current_pattern = [current_time]
                    self.pattern_start_time = current_time
                    print(f"\n🎤 Knock detected! Starting pattern...")
                else:
                    # Add knock to current pattern
                    self.current_pattern.append(current_time)
                    knock_number = len(self.current_pattern)
                    time_since_start = current_time - self.pattern_start_time
                    print(f"🎤 Knock #{knock_number} (at {time_since_start:.2f}s)")
                
                self.peak_buffer.append(current_time)
        
        # Check if pattern is complete (no knock for pattern_timeout)
        if self.current_pattern and current_time - self.last_knock_time > self.pattern_timeout:
            if len(self.current_pattern) >= 2:
                # Calculate intervals
                intervals = self.calculate_intervals(self.current_pattern)
                
                if self.recording_mode:
                    # Save recorded pattern
                    self.recorded_pattern = intervals
                    print(f"\n📝 Pattern recorded: {[f'{i:.2f}' for i in intervals]}")
                    print("   Use this pattern to create new actions!")
                    self.recording_mode = False
                else:
                    # Try to match pattern
                    print(f"\n🔍 Analyzing pattern: {[f'{i:.2f}s' for i in intervals]}")
                    matched = self.match_pattern(intervals)
                    
                    if matched:
                        self.perform_action(matched)
                    else:
                        print("❌ No pattern matched. Try again or use 'record' mode.")
            
            # Reset pattern
            self.current_pattern = []
    
    def display_visual(self):
        """Display visual window"""
        while self.running:
            # Create and show visual window
            canvas = self.draw_visual_window()
            cv2.imshow('Knock Detector', canvas)
            
            # Check for key press
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                self.running = False
                break
        
        cv2.destroyAllWindows()
    
    def run(self):
        """Start the knock detector"""
        print("🎤 Secret Knock Detector Starting...")
        print("-" * 50)
        print("Initializing microphone...")
        
        # Test microphone
        try:
            devices = sd.query_devices()
            default_input = sd.query_devices(kind='input')
            print(f"Using: {default_input['name']}")
            print(f"Sample Rate: {self.sample_rate} Hz")
            print(f"Knock Threshold: {self.threshold}")
            print("-" * 50)
        except Exception as e:
            print(f"Error accessing microphone: {e}")
            return
        
        print("\n✅ Ready! Start knocking on your computer!")
        print("💡 Tip: Knock on the desk/table near your computer for best results")
        print("-" * 50)
        
        self.running = True
        
        # Start audio stream in a separate thread
        def audio_thread():
            try:
                with sd.InputStream(
                    channels=self.channels,
                    samplerate=self.sample_rate,
                    blocksize=self.chunk_size,
                    callback=self.audio_callback
                ):
                    while self.running:
                        time.sleep(0.1)
            except Exception as e:
                print(f"\n❌ Audio Error: {e}")
                self.running = False
        
        audio_stream = threading.Thread(target=audio_thread, daemon=True)
        audio_stream.start()
        
        # Give audio stream time to start
        time.sleep(0.5)
        
        # Run visual display in main thread
        try:
            self.display_visual()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping knock detector...")
            self.running = False
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.running = False
        
        print("👋 Goodbye!")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║           🚪 SECRET KNOCK DETECTOR 🔊                      ║
    ║                                                           ║
    ║  Knock on your computer in specific patterns to trigger  ║
    ║  different actions!                                       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    detector = KnockDetector()
    
    # You can adjust sensitivity here
    print("🔧 Settings:")
    print(f"   Volume Threshold: {detector.threshold} (higher = less sensitive)")
    print(f"   Spike Threshold: {detector.spike_threshold} (detects sudden increases)")
    print(f"   Pattern timeout: {detector.pattern_timeout}s")
    print(f"\n💡 Tip: Knocks create sudden spikes. Talking/music won't trigger it!")
    print()
    
    try:
        detector.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

