import cv2
import mediapipe as mp
import numpy as np

class EyeTracker:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Eye landmark indices
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        self.LEFT_IRIS = [474, 475, 476, 477]
        self.RIGHT_IRIS = [469, 470, 471, 472]
        
    def get_eye_position(self, landmarks, eye_indices, iris_indices, frame_width, frame_height):
        """Calculate eye center and iris position"""
        # Get eye corners
        eye_points = []
        for idx in eye_indices:
            x = int(landmarks[idx].x * frame_width)
            y = int(landmarks[idx].y * frame_height)
            eye_points.append((x, y))
        
        # Get iris center
        iris_points = []
        for idx in iris_indices:
            x = int(landmarks[idx].x * frame_width)
            y = int(landmarks[idx].y * frame_height)
            iris_points.append((x, y))
        
        if iris_points:
            iris_center = np.mean(iris_points, axis=0).astype(int)
        else:
            iris_center = None
            
        # Calculate eye bounding box center
        if eye_points:
            eye_center = np.mean(eye_points, axis=0).astype(int)
            eye_left = min(p[0] for p in eye_points)
            eye_right = max(p[0] for p in eye_points)
            eye_top = min(p[1] for p in eye_points)
            eye_bottom = max(p[1] for p in eye_points)
        else:
            eye_center = None
            eye_left = eye_right = eye_top = eye_bottom = 0
            
        return eye_center, iris_center, (eye_left, eye_right, eye_top, eye_bottom)
    
    def get_gaze_direction(self, eye_center, iris_center, eye_bounds):
        """Determine gaze direction based on iris position relative to eye"""
        if eye_center is None or iris_center is None:
            return "Unknown", (0, 0)
        
        eye_left, eye_right, eye_top, eye_bottom = eye_bounds
        eye_width = eye_right - eye_left
        eye_height = eye_bottom - eye_top
        
        if eye_width == 0 or eye_height == 0:
            return "Unknown", (0, 0)
        
        # Calculate relative position of iris within eye
        # Normalize to -1 to 1 range
        relative_x = (iris_center[0] - eye_center[0]) / (eye_width / 2)
        relative_y = (iris_center[1] - eye_center[1]) / (eye_height / 2)
        
        # Clamp values
        relative_x = np.clip(relative_x, -1, 1)
        relative_y = np.clip(relative_y, -1, 1)
        
        # Determine direction
        direction_text = []
        
        # Vertical direction
        if relative_y < -0.15:
            direction_text.append("Up")
        elif relative_y > 0.15:
            direction_text.append("Down")
        
        # Horizontal direction
        if relative_x < -0.15:
            direction_text.append("Left")
        elif relative_x > 0.15:
            direction_text.append("Right")
        
        if not direction_text:
            direction_text.append("Center")
        
        return " ".join(direction_text), (relative_x, relative_y)
    
    def draw_eye_info(self, frame, eye_center, iris_center, eye_bounds, label, color):
        """Draw eye tracking visualization"""
        if eye_center is not None:
            # Draw eye center
            cv2.circle(frame, tuple(eye_center), 3, (0, 255, 0), -1)
            
        if iris_center is not None:
            # Draw iris center
            cv2.circle(frame, tuple(iris_center), 5, color, 2)
            
            # Draw line from eye center to iris
            if eye_center is not None:
                cv2.line(frame, tuple(eye_center), tuple(iris_center), color, 2)
        
        # Draw eye bounding box
        eye_left, eye_right, eye_top, eye_bottom = eye_bounds
        if eye_left and eye_right and eye_top and eye_bottom:
            cv2.rectangle(frame, (eye_left, eye_top), (eye_right, eye_bottom), (100, 100, 100), 1)
    
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
        
        print("Eye Tracker Started!")
        print("Press 'q' to quit")
        print("-" * 50)
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame")
                continue
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.face_mesh.process(rgb_frame)
            
            frame_height, frame_width = frame.shape[:2]
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    landmarks = face_landmarks.landmark
                    
                    # Get left eye info
                    left_eye_center, left_iris_center, left_eye_bounds = self.get_eye_position(
                        landmarks, self.LEFT_EYE, self.LEFT_IRIS, frame_width, frame_height
                    )
                    
                    # Get right eye info
                    right_eye_center, right_iris_center, right_eye_bounds = self.get_eye_position(
                        landmarks, self.RIGHT_EYE, self.RIGHT_IRIS, frame_width, frame_height
                    )
                    
                    # Draw eye tracking visualizations
                    self.draw_eye_info(frame, left_eye_center, left_iris_center, 
                                     left_eye_bounds, "Left", (255, 0, 0))
                    self.draw_eye_info(frame, right_eye_center, right_iris_center, 
                                     right_eye_bounds, "Right", (0, 0, 255))
                    
                    # Calculate gaze direction (using average of both eyes)
                    left_direction, left_relative = self.get_gaze_direction(
                        left_eye_center, left_iris_center, left_eye_bounds
                    )
                    right_direction, right_relative = self.get_gaze_direction(
                        right_eye_center, right_iris_center, right_eye_bounds
                    )
                    
                    # Average relative positions
                    avg_relative_x = (left_relative[0] + right_relative[0]) / 2
                    avg_relative_y = (left_relative[1] + right_relative[1]) / 2
                    
                    # Draw gaze indicator
                    self.draw_gaze_indicator(frame, avg_relative_x, avg_relative_y)
                    
                    # Display gaze information
                    gaze_text = f"Looking: {left_direction}"
                    cv2.putText(frame, gaze_text, (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    # Display coordinates
                    coord_text = f"X: {avg_relative_x:.2f}, Y: {avg_relative_y:.2f}"
                    cv2.putText(frame, coord_text, (10, 70), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            else:
                cv2.putText(frame, "No face detected", (10, 30), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (10, frame_height - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Show the frame
            cv2.imshow('Eye Tracker', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\nEye Tracker stopped.")

if __name__ == "__main__":
    tracker = EyeTracker()
    tracker.run()

