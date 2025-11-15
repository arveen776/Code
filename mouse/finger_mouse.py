"""
Finger Tracking Mouse Controller
Tracks finger movement via webcam using color-based tracking
Works with any Python version - no MediaPipe required!
"""

import cv2
import pyautogui
import numpy as np
import time

# Disable pyautogui failsafe for smoother operation
pyautogui.FAILSAFE = False

# Screen dimensions for mapping
screen_width, screen_height = pyautogui.size()

# Configuration
SMOOTHING = 0.7  # Smoothing factor (0-1), higher = more smoothing
MOVEMENT_SCALE = 2.0  # Scale factor for movement sensitivity

class FingerMouse:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Previous position for relative movement
        self.prev_x = None
        self.prev_y = None
        self.smooth_x = None
        self.smooth_y = None
        
        # Color range for tracking (HSV)
        # Default: bright color (yellow/orange/red works well)
        # You can adjust these values to track different colored objects
        self.lower_bound = np.array([20, 100, 100])  # Lower HSV bound
        self.upper_bound = np.array([30, 255, 255])  # Upper HSV bound
        
        # Tracking mode: 'color' for color-based tracking, 'motion' for motion-based
        self.tracking_mode = 'motion'  # Start with motion tracking (no colored marker needed)
        
        # For motion tracking
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.kernel = np.ones((5, 5), np.uint8)
        
        print("Finger Mouse Controller initialized!")
        print("Instructions:")
        print("- Hold your finger/object in front of the camera")
        print("- Move it to control the mouse")
        print("- Press 'c' to calibrate color tracking (detects object under cursor)")
        print("- Press 'm' to toggle between motion and color tracking")
        print("- Press 'q' to quit")
        print("- Press 'r' to reset mouse position")
        
    def calibrate_color(self, frame):
        """Calibrate color tracking by detecting the dominant color at center"""
        h, w = frame.shape[:2]
        center_region = frame[h//4:3*h//4, w//4:3*w//4]
        
        # Convert to HSV
        hsv_center = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
        
        # Get average color
        avg_hue = np.median(hsv_center[:, :, 0])
        avg_sat = np.median(hsv_center[:, :, 1])
        avg_val = np.median(hsv_center[:, :, 2])
        
        # Set color range around detected color
        hue_range = 15
        sat_range = 50
        val_range = 50
        
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
        
        print(f"Color calibrated! Lower: {self.lower_bound}, Upper: {self.upper_bound}")
        
    def track_color(self, frame):
        """Track object using color-based detection"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower_bound, self.upper_bound)
        mask = cv2.erode(mask, self.kernel, iterations=2)
        mask = cv2.dilate(mask, self.kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Get center of contour
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
                return x, y, mask
        
        return None, None, mask
    
    def track_motion(self, frame):
        """Track object using motion detection"""
        fg_mask = self.bg_subtractor.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, self.kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, self.kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get largest contour (moving object)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Filter small contours (noise)
            if cv2.contourArea(largest_contour) > 500:
                # Get center of contour
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    x = int(M["m10"] / M["m00"])
                    y = int(M["m01"] / M["m00"])
                    return x, y, fg_mask
        
        return None, None, fg_mask
        
    def run(self):
        frame_count = 0
        start_time = time.time()
        calibration_countdown = 0
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Track object based on mode
            if self.tracking_mode == 'color':
                x, y, mask = self.track_color(frame)
                display_frame = cv2.bitwise_and(frame, frame, mask=mask)
            else:  # motion tracking
                x, y, mask = self.track_motion(frame)
                display_frame = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            
            # Draw tracking point and calculate mouse movement
            if x is not None and y is not None:
                # Draw circle at tracked point
                cv2.circle(frame, (x, y), 15, (0, 255, 0), 2)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
                
                # Calculate mouse movement
                if self.prev_x is not None and self.prev_y is not None:
                    # Calculate relative movement
                    dx = (x - self.prev_x) * MOVEMENT_SCALE
                    dy = (y - self.prev_y) * MOVEMENT_SCALE
                    
                    # Apply smoothing
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
                    
                    # Keep within screen bounds
                    new_x = max(0, min(screen_width - 1, new_x))
                    new_y = max(0, min(screen_height - 1, new_y))
                    
                    pyautogui.moveTo(new_x, new_y, duration=0.01)
                
                # Update previous position
                self.prev_x = x
                self.prev_y = y
            else:
                # Reset when object is not detected
                self.prev_x = None
                self.prev_y = None
                self.smooth_x = None
                self.smooth_y = None
            
            # Handle calibration countdown
            if calibration_countdown > 0:
                calibration_countdown -= 1
                cv2.putText(frame, f"Calibrating in {calibration_countdown//10}...", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                if calibration_countdown == 1:
                    self.calibrate_color(frame)
            
            # Display FPS
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                # Reset counters every 300 frames to avoid overflow
                if frame_count >= 300:
                    frame_count = 0
                    start_time = time.time()
            
            # Add instructions to frame
            mode_text = "Color Tracking" if self.tracking_mode == 'color' else "Motion Tracking"
            cv2.putText(frame, f"Mode: {mode_text}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Move finger/object to control mouse", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(frame, "'c'=calibrate, 'm'=toggle mode, 'q'=quit, 'r'=reset", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Finger Mouse Controller', frame)
            
            # Show mask/debug view (optional)
            if self.tracking_mode == 'color':
                cv2.imshow('Mask View', mask)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Reset to center of screen
                pyautogui.moveTo(screen_width // 2, screen_height // 2)
                print("Mouse position reset to center")
            elif key == ord('c'):
                # Start calibration countdown
                calibration_countdown = 30
                print("Calibration starting in 3 seconds...")
            elif key == ord('m'):
                # Toggle tracking mode
                self.tracking_mode = 'color' if self.tracking_mode == 'motion' else 'motion'
                if self.tracking_mode == 'motion':
                    # Reset background subtractor when switching to motion mode
                    self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
                print(f"Switched to {self.tracking_mode} tracking")
        
        self.cleanup()
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("Finger Mouse Controller stopped.")

if __name__ == "__main__":
    try:
        controller = FingerMouse()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

