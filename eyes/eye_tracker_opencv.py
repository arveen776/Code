import cv2
import numpy as np

class EyeTrackerOpenCV:
    def __init__(self):
        # Load pre-trained Haar Cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # For pupil detection
        self.pupil_params = cv2.SimpleBlobDetector_Params()
        self.pupil_params.filterByArea = True
        self.pupil_params.maxArea = 1500
        self.pupil_params.minArea = 10
        self.pupil_params.filterByCircularity = True
        self.pupil_params.minCircularity = 0.7
        self.pupil_params.filterByConvexity = True
        self.pupil_params.minConvexity = 0.8
        self.pupil_params.filterByInertia = True
        self.pupil_params.minInertiaRatio = 0.5
        
        self.detector = cv2.SimpleBlobDetector_create(self.pupil_params)
        
        # Smoothing buffer for gaze position
        self.gaze_history = []
        self.history_size = 5
        
    def detect_pupil(self, eye_roi):
        """Detect pupil in eye region"""
        # Convert to grayscale if needed
        if len(eye_roi.shape) == 3:
            gray_eye = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)
        else:
            gray_eye = eye_roi
        
        # Apply thresholding
        _, threshold = cv2.threshold(gray_eye, 50, 255, cv2.THRESH_BINARY_INV)
        
        # Apply blur to reduce noise
        threshold = cv2.medianBlur(threshold, 5)
        
        # Detect pupil
        keypoints = self.detector.detect(threshold)
        
        if keypoints:
            # Return the largest keypoint (likely the pupil)
            largest = max(keypoints, key=lambda k: k.size)
            return (int(largest.pt[0]), int(largest.pt[1]))
        
        # Fallback: find darkest region
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray_eye)
        return min_loc
    
    def get_gaze_direction(self, pupil_pos, eye_region):
        """Determine gaze direction based on pupil position"""
        eye_x, eye_y, eye_w, eye_h = eye_region
        
        # Calculate relative position
        center_x = eye_w / 2
        center_y = eye_h / 2
        
        # Normalized position (-1 to 1)
        relative_x = (pupil_pos[0] - center_x) / (eye_w / 2)
        relative_y = (pupil_pos[1] - center_y) / (eye_h / 2)
        
        # Clamp values
        relative_x = np.clip(relative_x, -1, 1)
        relative_y = np.clip(relative_y, -1, 1)
        
        return relative_x, relative_y
    
    def get_direction_text(self, relative_x, relative_y):
        """Convert relative position to direction text"""
        direction_text = []
        
        # Vertical direction
        if relative_y < -0.2:
            direction_text.append("Up")
        elif relative_y > 0.2:
            direction_text.append("Down")
        
        # Horizontal direction
        if relative_x < -0.2:
            direction_text.append("Left")
        elif relative_x > 0.2:
            direction_text.append("Right")
        
        if not direction_text:
            direction_text.append("Center")
        
        return " ".join(direction_text)
    
    def smooth_gaze(self, relative_x, relative_y):
        """Smooth gaze position using moving average"""
        self.gaze_history.append((relative_x, relative_y))
        
        if len(self.gaze_history) > self.history_size:
            self.gaze_history.pop(0)
        
        avg_x = np.mean([g[0] for g in self.gaze_history])
        avg_y = np.mean([g[1] for g in self.gaze_history])
        
        return avg_x, avg_y
    
    def draw_gaze_indicator(self, frame, relative_x, relative_y):
        """Draw a gaze direction indicator in the corner"""
        indicator_size = 150
        indicator_x = frame.shape[1] - indicator_size - 20
        indicator_y = 20
        
        # Draw indicator background
        cv2.rectangle(frame, 
                     (indicator_x, indicator_y), 
                     (indicator_x + indicator_size, indicator_y + indicator_size),
                     (50, 50, 50), -1)
        
        # Draw center point
        center_x = indicator_x + indicator_size // 2
        center_y = indicator_y + indicator_size // 2
        cv2.circle(frame, (center_x, center_y), 3, (200, 200, 200), -1)
        
        # Draw gaze point
        gaze_x = int(center_x + relative_x * (indicator_size // 2 - 10))
        gaze_y = int(center_y + relative_y * (indicator_size // 2 - 10))
        cv2.circle(frame, (gaze_x, gaze_y), 8, (0, 255, 255), -1)
        
        # Draw cross-hairs
        cv2.line(frame, (center_x, indicator_y), (center_x, indicator_y + indicator_size), (100, 100, 100), 1)
        cv2.line(frame, (indicator_x, center_y), (indicator_x + indicator_size, center_y), (100, 100, 100), 1)
        
        # Label
        cv2.putText(frame, "Gaze Direction", 
                   (indicator_x, indicator_y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def run(self):
        """Main loop to run eye tracking"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Eye Tracker Started! (OpenCV Version)")
        print("Press 'q' to quit")
        print("-" * 50)
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame")
                continue
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.3, 
                minNeighbors=5,
                minSize=(100, 100)
            )
            
            frame_height, frame_width = frame.shape[:2]
            
            if len(faces) > 0:
                # Use the largest face
                face = max(faces, key=lambda f: f[2] * f[3])
                fx, fy, fw, fh = face
                
                # Draw face rectangle
                cv2.rectangle(frame, (fx, fy), (fx + fw, fy + fh), (255, 255, 0), 2)
                
                # Region of interest for eyes (upper half of face)
                roi_gray = gray[fy:fy + fh, fx:fx + fw]
                roi_color = frame[fy:fy + fh, fx:fx + fw]
                
                # Detect eyes
                eyes = self.eye_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.1,
                    minNeighbors=10,
                    minSize=(30, 30)
                )
                
                gaze_positions = []
                
                for i, (ex, ey, ew, eh) in enumerate(eyes[:2]):  # Process up to 2 eyes
                    # Draw eye rectangle
                    cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
                    
                    # Extract eye region
                    eye_roi = roi_gray[ey:ey + eh, ex:ex + ew]
                    
                    # Detect pupil
                    pupil_pos = self.detect_pupil(eye_roi)
                    
                    # Draw pupil
                    pupil_x = fx + ex + pupil_pos[0]
                    pupil_y = fy + ey + pupil_pos[1]
                    cv2.circle(frame, (pupil_x, pupil_y), 5, (0, 0, 255), -1)
                    
                    # Calculate gaze direction
                    relative_x, relative_y = self.get_gaze_direction(pupil_pos, (ex, ey, ew, eh))
                    gaze_positions.append((relative_x, relative_y))
                
                if gaze_positions:
                    # Average gaze from both eyes
                    avg_x = np.mean([g[0] for g in gaze_positions])
                    avg_y = np.mean([g[1] for g in gaze_positions])
                    
                    # Apply smoothing
                    smooth_x, smooth_y = self.smooth_gaze(avg_x, avg_y)
                    
                    # Get direction text
                    direction = self.get_direction_text(smooth_x, smooth_y)
                    
                    # Draw gaze indicator
                    self.draw_gaze_indicator(frame, smooth_x, smooth_y)
                    
                    # Display information
                    gaze_text = f"Looking: {direction}"
                    cv2.putText(frame, gaze_text, (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    coord_text = f"X: {smooth_x:.2f}, Y: {smooth_y:.2f}"
                    cv2.putText(frame, coord_text, (10, 70), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Eye count
                    eye_count_text = f"Eyes detected: {len(eyes[:2])}"
                    cv2.putText(frame, eye_count_text, (10, 110), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
                else:
                    cv2.putText(frame, "Eyes detected but tracking failed", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            else:
                cv2.putText(frame, "No face detected", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (10, frame_height - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Show the frame
            cv2.imshow('Eye Tracker (OpenCV)', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\nEye Tracker stopped.")

if __name__ == "__main__":
    tracker = EyeTrackerOpenCV()
    tracker.run()

