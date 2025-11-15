"""
Head/Face Tracking Mouse Controller
Tracks your head/face position and translates it to mouse cursor movement
Very natural - you look where you want the cursor to go!
"""

import cv2
import pyautogui
import numpy as np
import time

# Try to import dlib (optional)
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False
    print("Note: dlib not available. Using OpenCV face detection (still works well!)")

# Disable pyautogui failsafe for smoother operation
pyautogui.FAILSAFE = False

# Screen dimensions for mapping
screen_width, screen_height = pyautogui.size()

# Configuration
SMOOTHING = 0.85  # Smoothing factor (0-1), higher = more smoothing
FACE_DEAD_ZONE = 5  # Dead zone in pixels (ignores tiny movements) - reduced for more sensitivity
SCALE_FACTOR = 12.0  # Scale factor for movement sensitivity - increased significantly for small head movements

class HeadMouse:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Try to initialize dlib face detector (optional, works without it)
        self.use_dlib = False
        self.use_landmarks = False
        
        if DLIB_AVAILABLE:
            try:
                self.detector = dlib.get_frontal_face_detector()
                # Try to load predictor (optional - download from dlib.net if you want more precision)
                try:
                    self.predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
                    self.use_landmarks = True
                    print("Using dlib with face landmarks (high precision)")
                except:
                    print("Using dlib basic face detection (good precision)")
                self.use_dlib = True
            except Exception as e:
                print(f"Could not initialize dlib: {e}")
                self.use_dlib = False
        
        if not self.use_dlib:
            print("Using OpenCV face detection (works well, no extra setup needed!)")
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Face tracking variables
        self.face_center_x = None
        self.face_center_y = None
        self.prev_face_x = None
        self.prev_face_y = None
        self.smooth_x = None
        self.smooth_y = None
        
        # Calibration
        self.reference_x = None
        self.reference_y = None
        self.calibrated = False
        
        print("\n" + "="*50)
        print("HEAD TRACKING MOUSE CONTROLLER")
        print("="*50)
        print("Instructions:")
        print("- Position your face in front of the camera")
        print("- Move your head to control the mouse cursor")
        print("- Press 'c' to calibrate (set center position)")
        print("- Press 'q' to quit")
        print("- Press 'r' to reset mouse to screen center")
        print("="*50 + "\n")
        
    def detect_face_dlib(self, frame):
        """Detect face using dlib (more accurate)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) > 0:
            face = faces[0]  # Use first detected face
            
            if self.use_landmarks:
                # Get face landmarks
                landmarks = self.predictor(gray, face)
                
                # Get nose tip (landmark 30) - best for tracking head direction
                nose_x = landmarks.part(30).x
                nose_y = landmarks.part(30).y
                
                # Also use face center for stability
                x = face.left()
                y = face.top()
                w = face.width()
                h = face.height()
                
                # Weighted average: 70% nose tip, 30% face center
                center_x = int(x + w/2)
                center_y = int(y + h/2)
                
                final_x = int(nose_x * 0.7 + center_x * 0.3)
                final_y = int(nose_y * 0.7 + center_y * 0.3)
                
                return final_x, final_y, (x, y, w, h), landmarks
            else:
                # Basic face detection without landmarks
                x = face.left()
                y = face.top()
                w = face.width()
                h = face.height()
                center_x = int(x + w/2)
                center_y = int(y + h/2)
                return center_x, center_y, (x, y, w, h), None
        
        return None, None, None, None
    
    def detect_face_opencv(self, frame):
        """Detect face using OpenCV (fallback)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            x, y, w, h = faces[0]  # Use first detected face
            center_x = int(x + w/2)
            center_y = int(y + h/2)
            return center_x, center_y, (x, y, w, h), None
        
        return None, None, None, None
    
    def calibrate(self, face_x, face_y):
        """Set current face position as reference center"""
        self.reference_x = face_x
        self.reference_y = face_y
        self.calibrated = True
        print(f"Calibrated! Reference position: ({face_x}, {face_y})")
        print("Move your head to control the cursor now.")
    
    def run(self):
        frame_count = 0
        start_time = time.time()
        
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            display_frame = frame.copy()
            
            # Detect face
            if self.use_dlib:
                face_x, face_y, face_rect, landmarks = self.detect_face_dlib(frame)
            else:
                face_x, face_y, face_rect, landmarks = self.detect_face_opencv(frame)
            
            if face_x is not None and face_y is not None:
                # Draw face rectangle
                if face_rect:
                    x, y, w, h = face_rect
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Draw face center point
                cv2.circle(display_frame, (face_x, face_y), 5, (0, 255, 0), -1)
                cv2.circle(display_frame, (face_x, face_y), 15, (0, 255, 0), 2)
                
                # Draw landmarks if available
                if landmarks:
                    for i in range(68):
                        point = landmarks.part(i)
                        cv2.circle(display_frame, (point.x, point.y), 2, (255, 0, 0), -1)
                    
                    # Highlight nose tip
                    nose = landmarks.part(30)
                    cv2.circle(display_frame, (nose.x, nose.y), 5, (255, 255, 0), -1)
                
                # Calibrate on first detection or when 'c' is pressed
                if not self.calibrated:
                    self.calibrate(face_x, face_y)
                    self.prev_face_x = face_x
                    self.prev_face_y = face_y
                else:
                    # Calculate movement relative to reference
                    if self.prev_face_x is not None and self.prev_face_y is not None:
                        # Relative movement from reference - highly sensitive for small head movements
                        dx = (face_x - self.reference_x) * SCALE_FACTOR
                        dy = (face_y - self.reference_y) * SCALE_FACTOR
                        
                        # Apply dead zone (reduced for more sensitivity)
                        if abs(dx) < FACE_DEAD_ZONE:
                            dx = 0
                        if abs(dy) < FACE_DEAD_ZONE:
                            dy = 0
                        
                        # Apply smoothing
                        if self.smooth_x is None:
                            self.smooth_x = dx
                            self.smooth_y = dy
                        else:
                            self.smooth_x = self.smooth_x * SMOOTHING + dx * (1 - SMOOTHING)
                            self.smooth_y = self.smooth_y * SMOOTHING + dy * (1 - SMOOTHING)
                        
                        # Calculate screen position (absolute mapping)
                        screen_center_x = screen_width // 2
                        screen_center_y = screen_height // 2
                        
                        # Map face movement to screen movement
                        new_x = int(screen_center_x + self.smooth_x)
                        new_y = int(screen_center_y + self.smooth_y)
                        
                        # Keep within screen bounds
                        new_x = max(0, min(screen_width - 1, new_x))
                        new_y = max(0, min(screen_height - 1, new_y))
                        
                        # Move mouse
                        pyautogui.moveTo(new_x, new_y, duration=0.0)
                    
                    # Update previous position
                    self.prev_face_x = face_x
                    self.prev_face_y = face_y
            else:
                # Reset when face is not detected
                self.prev_face_x = None
                self.prev_face_y = None
                self.smooth_x = None
                self.smooth_y = None
                
                cv2.putText(display_frame, "No face detected", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Display status
            status = "Calibrated" if self.calibrated else "Not Calibrated"
            cv2.putText(display_frame, f"Status: {status}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(display_frame, "Press 'c' to calibrate, 'q' to quit", (10, 60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Head Tracking Mouse Controller', display_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                if face_x is not None and face_y is not None:
                    self.calibrate(face_x, face_y)
                else:
                    print("Face not detected! Cannot calibrate.")
            elif key == ord('r'):
                pyautogui.moveTo(screen_width // 2, screen_height // 2)
                print("Mouse position reset to center")
        
        self.cleanup()
    
    def cleanup(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("Head Mouse Controller stopped.")

if __name__ == "__main__":
    try:
        controller = HeadMouse()
        controller.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

