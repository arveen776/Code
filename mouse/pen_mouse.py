"""
Pen/Stylus Tracking Mouse Controller
Track any pen, stylus, or pointing object you hold
Very natural - just point at what you want to control!
"""

import cv2
import pyautogui
import numpy as np
import time

# Disable pyautogui failsafe
pyautogui.FAILSAFE = False

# Screen dimensions
screen_width, screen_height = pyautogui.size()

# Configuration
SMOOTHING = 0.8  # Smoothing factor
MOVEMENT_SCALE = 2.5  # Movement sensitivity
DEAD_ZONE = 5  # Dead zone in pixels
MIN_CONTOUR_AREA = 200  # Minimum area to detect as pen

class PenMouse:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Tracking variables
        self.prev_x = None
        self.prev_y = None
        self.smooth_x = None
        self.smooth_y = None
        
        # Color tracking for pen (calibrate by pressing 'c')
        self.lower_bound = np.array([0, 50, 50])
        self.upper_bound = np.array([180, 255, 255])
        self.calibrated = False
        
        # Background subtractor for motion tracking
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, detectShadows=False)
        self.kernel = np.ones((5, 5), np.uint8)
        
        # Tracking mode
        self.tracking_mode = 'color'  # 'color' or 'motion'
        
        print("\n" + "="*50)
        print("PEN/STYLUS TRACKING MOUSE CONTROLLER")
        print("="*50)
        print("Instructions:")
        print("- Hold a pen, marker, or any pointing object")
        print("- Press 'c' to calibrate color tracking (point at pen for 3 seconds)")
        print("- Move the pen tip to control the cursor")
        print("- Press 'm' to toggle between color and motion tracking")
        print("- Press 'q' to quit")
        print("="*50 + "\n")
    
    def calibrate_color(self, frame):
        """Calibrate to track the pen color"""
        h, w = frame.shape[:2]
        # Get center region where pen tip should be
        center_region = frame[h//3:2*h//3, w//3:2*w//3]
        
        hsv = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
        
        # Get median color
        avg_hue = np.median(hsv[:, :, 0])
        avg_sat = np.median(hsv[:, :, 1])
        avg_val = np.median(hsv[:, :, 2])
        
        # Set color range
        hue_range = 20
        sat_range = 60
        val_range = 60
        
        self.lower_bound = np.array([
            max(0, avg_hue - hue_range),
            max(0, avg_sat - sat_range),
            max(0, avg_val - val_range)
        ])
        
        self.upper_bound = np.array([
            min(179, avg_hue + hue_range),
            min(255, avg_sat + sat_range),
            min(255, avg_val + val_range)
        ])
        
        self.calibrated = True
        print(f"Color calibrated! Tracking range: {self.lower_bound} - {self.upper_bound}")
    
    def track_color(self, frame):
        """Track pen using color"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
        
        # Noise reduction
        mask = cv2.medianBlur(mask, 5)
        mask = cv2.erode(mask, self.kernel, iterations=1)
        mask = cv2.dilate(mask, self.kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the highest (topmost) contour - likely the pen tip
            valid_contours = [c for c in contours if cv2.contourArea(c) > MIN_CONTOUR_AREA]
            
            if valid_contours:
                # Find topmost point (pen tip)
                best_contour = None
                min_y = float('inf')
                topmost_point = None
                
                for contour in valid_contours:
                    topmost = tuple(contour[contour[:, :, 1].argmin()][0])
                    if topmost[1] < min_y:
                        min_y = topmost[1]
                        best_contour = contour
                        topmost_point = topmost
                
                if topmost_point:
                    return topmost_point[0], topmost_point[1], mask
        
        return None, None, mask
    
    def track_motion(self, frame):
        """Track pen using motion"""
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        fg_mask = self.bg_subtractor.apply(blurred)
        
        # Morphological operations
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            valid_contours = [c for c in contours if MIN_CONTOUR_AREA < cv2.contourArea(c) < 2000]
            
            if valid_contours:
                # Get topmost point (pen tip)
                best_contour = None
                min_y = float('inf')
                
                for contour in valid_contours:
                    topmost = tuple(contour[contour[:, :, 1].argmin()][0])
                    if topmost[1] < min_y:
                        min_y = topmost[1]
                        best_contour = contour
                
                if best_contour:
                    topmost = tuple(best_contour[best_contour[:, :, 1].argmin()][0])
                    return topmost[0], topmost[1], fg_mask
        
        return None, None, fg_mask
    
    def run(self):
        calibration_countdown = 0
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            # Track pen
            if self.tracking_mode == 'color':
                x, y, mask = self.track_color(frame)
            else:
                x, y, mask = self.track_motion(frame)
            
            # Handle calibration countdown
            if calibration_countdown > 0:
                calibration_countdown -= 1
                cv2.putText(frame, f"Calibrating in {calibration_countdown//10}...", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                if calibration_countdown == 1 and self.tracking_mode == 'color':
                    self.calibrate_color(frame)
            
            if x is not None and y is not None:
                # Draw tracking point
                cv2.circle(frame, (x, y), 8, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                
                # Calculate mouse movement
                if self.prev_x is not None and self.prev_y is not None:
                    dx = (x - self.prev_x) * MOVEMENT_SCALE
                    dy = (y - self.prev_y) * MOVEMENT_SCALE
                    
                    # Dead zone
                    if abs(dx) < DEAD_ZONE:
                        dx = 0
                    if abs(dy) < DEAD_ZONE:
                        dy = 0
                    
                    # Smoothing
                    if self.smooth_x is None:
                        self.smooth_x = dx
                        self.smooth_y = dy
                    else:
                        self.smooth_x = self.smooth_x * SMOOTHING + dx * (1 - SMOOTHING)
                        self.smooth_y = self.smooth_y * SMOOTHING + dy * (1 - SMOOTHING)
                    
                    # Move mouse
                    current_x, current_y = pyautogui.position()
                    new_x = int(current_x + self.smooth_x)
                    new_y = int(current_y + self.smooth_y)
                    
                    new_x = max(0, min(screen_width - 1, new_x))
                    new_y = max(0, min(screen_height - 1, new_y))
                    
                    pyautogui.moveTo(new_x, new_y, duration=0.0)
                
                self.prev_x = x
                self.prev_y = y
            else:
                self.prev_x = None
                self.prev_y = None
                self.smooth_x = None
                self.smooth_y = None
            
            # Display info
            mode_text = "Color Tracking" if self.tracking_mode == 'color' else "Motion Tracking"
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "'c'=calibrate, 'm'=toggle, 'q'=quit", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            if not self.calibrated and self.tracking_mode == 'color':
                cv2.putText(frame, "Press 'c' to calibrate color!", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            cv2.imshow('Pen Tracking Mouse Controller', frame)
            
            # Handle input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                if self.tracking_mode == 'color':
                    calibration_countdown = 30
                    print("Calibration starting in 3 seconds...")
                else:
                    print("Calibration only works in color tracking mode")
            elif key == ord('m'):
                self.tracking_mode = 'color' if self.tracking_mode == 'motion' else 'motion'
                if self.tracking_mode == 'motion':
                    self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, detectShadows=False)
                print(f"Switched to {self.tracking_mode} tracking")
        
        self.cleanup()
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("Pen Mouse Controller stopped.")

if __name__ == "__main__":
    try:
        controller = PenMouse()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

