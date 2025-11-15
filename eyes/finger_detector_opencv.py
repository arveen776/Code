import cv2
import numpy as np
import time

class FingerDetectorOpenCV:
    def __init__(self):
        # For background subtraction and skin detection
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        
        # Action cooldown to prevent rapid triggering
        self.last_action_time = 0
        self.action_cooldown = 1.0  # seconds
        
        # Background color for visual feedback
        self.bg_color = (50, 50, 50)
        self.action_colors = {
            0: (50, 50, 50),      # Fist - Dark Gray
            1: (100, 100, 255),   # 1 finger - Red
            2: (100, 255, 100),   # 2 fingers - Green
            3: (255, 100, 100),   # 3 fingers - Blue
            4: (100, 255, 255),   # 4 fingers - Yellow
            5: (255, 100, 255),   # 5 fingers - Magenta
        }
        
        # ROI (Region of Interest) for hand detection
        self.roi_top = 100
        self.roi_bottom = 400
        self.roi_left = 350
        self.roi_right = 650
        
    def detect_skin(self, frame):
        """Detect skin color in the frame"""
        # Convert to HSV and YCrCb color spaces for better skin detection
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
        
        # HSV skin color range (wider range for better detection)
        lower_hsv = np.array([0, 15, 0], dtype=np.uint8)
        upper_hsv = np.array([25, 255, 255], dtype=np.uint8)
        mask_hsv = cv2.inRange(hsv, lower_hsv, upper_hsv)
        
        # YCrCb skin color range (works better in some lighting)
        lower_ycrcb = np.array([0, 133, 77], dtype=np.uint8)
        upper_ycrcb = np.array([255, 173, 127], dtype=np.uint8)
        mask_ycrcb = cv2.inRange(ycrcb, lower_ycrcb, upper_ycrcb)
        
        # Combine both masks
        mask = cv2.bitwise_or(mask_hsv, mask_ycrcb)
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        
        return mask
    
    def count_fingers_convexity(self, contour):
        """Count fingers using convexity defects method"""
        try:
            # Get convex hull
            hull = cv2.convexHull(contour, returnPoints=False)
            
            if len(hull) < 3:
                return 0
            
            # Get convexity defects
            defects = cv2.convexityDefects(contour, hull)
            
            if defects is None:
                return 0
            
            finger_count = 0
            
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                
                # Calculate the length of all sides of the triangle
                a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                
                # Calculate the angle
                angle = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
                
                # If angle is less than 90 degrees, it's a finger gap
                if angle <= np.pi / 2:
                    finger_count += 1
            
            # Number of fingers is defects + 1
            return min(finger_count + 1, 5)
        
        except Exception as e:
            return 0
    
    def count_fingers_contour(self, contour, drawing):
        """Count fingers using contour analysis"""
        try:
            # Get convex hull points
            hull = cv2.convexHull(contour, returnPoints=True)
            
            # Draw convex hull
            cv2.drawContours(drawing, [hull], -1, (0, 255, 0), 2)
            
            # Find convexity defects
            hull_indices = cv2.convexHull(contour, returnPoints=False)
            
            if len(hull_indices) < 3:
                return 0, drawing
            
            defects = cv2.convexityDefects(contour, hull_indices)
            
            if defects is None:
                return 0, drawing
            
            # Count fingers based on defects
            finger_count = 0
            
            # Get the center of the contour
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(drawing, (cx, cy), 10, (255, 0, 0), -1)
            else:
                return 0, drawing
            
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                far = tuple(contour[f][0])
                
                # Distance from defect point to contour
                distance = d / 256.0
                
                # Calculate the length of all sides of the triangle
                a = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = np.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = np.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                
                # Semi-perimeter
                s_p = (a + b + c) / 2
                
                # Calculate area using Heron's formula
                if s_p * (s_p - a) * (s_p - b) * (s_p - c) >= 0:
                    area = np.sqrt(s_p * (s_p - a) * (s_p - b) * (s_p - c))
                else:
                    continue
                
                # Calculate angle
                if b * c == 0:
                    continue
                    
                angle = np.arccos((b**2 + c**2 - a**2) / (2 * b * c))
                
                # Filter based on angle and distance
                if angle <= np.pi / 2 and distance > 30:
                    finger_count += 1
                    cv2.circle(drawing, far, 8, (0, 0, 255), -1)
            
            # Number of fingers is typically defects + 1
            finger_count = min(finger_count + 1, 5)
            
            return finger_count, drawing
            
        except Exception as e:
            return 0, drawing
    
    def perform_action(self, finger_count):
        """Perform action based on finger count"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_action_time < self.action_cooldown:
            return None
        
        actions = {
            0: "✊ Fist - No action",
            1: "☝️ One - Play/Pause",
            2: "✌️ Two - Volume Up",
            3: "🤟 Three - Volume Down",
            4: "🖖 Four - Next Track",
            5: "🖐️ Five - Previous Track"
        }
        
        action = actions.get(finger_count, "Unknown gesture")
        self.last_action_time = current_time
        
        # Update background color
        self.bg_color = self.action_colors.get(finger_count, (50, 50, 50))
        
        return action
    
    def draw_info_panel(self, frame, finger_count, action_text):
        """Draw information panel on the frame"""
        h, w = frame.shape[:2]
        
        # Create semi-transparent overlay
        overlay = frame.copy()
        
        # Draw colored background based on finger count
        cv2.rectangle(overlay, (0, 0), (w, 120), self.bg_color, -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Display finger count (large)
        finger_text = f"Fingers: {finger_count}"
        cv2.putText(frame, finger_text, (20, 60), 
                   cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 3)
        
        # Display action
        if action_text:
            cv2.putText(frame, action_text, (20, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def run(self):
        """Main loop to run finger detection"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Finger Detector Started! (OpenCV Version)")
        print("Place your hand in the green rectangle")
        print("Press 'q' to quit")
        print("-" * 50)
        print("\nGesture Actions:")
        print("  0 fingers (Fist) - No action")
        print("  1 finger - Play/Pause")
        print("  2 fingers - Volume Up")
        print("  3 fingers - Volume Down")
        print("  4 fingers - Next Track")
        print("  5 fingers - Previous Track")
        print("-" * 50)
        print("\nTIP: Spread your fingers wide for best detection!")
        
        last_action = None
        
        # Calibration frames
        calibration_frames = 30
        frame_count = 0
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print("Failed to grab frame")
                continue
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            frame_height, frame_width = frame.shape[:2]
            
            # Draw ROI rectangle
            cv2.rectangle(frame, (self.roi_left, self.roi_top), 
                         (self.roi_right, self.roi_bottom), (0, 255, 0), 2)
            
            # Extract ROI
            roi = frame[self.roi_top:self.roi_bottom, self.roi_left:self.roi_right]
            
            # Calibration phase
            if frame_count < calibration_frames:
                cv2.putText(frame, f"Calibrating... {calibration_frames - frame_count}", 
                           (self.roi_left, self.roi_top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Keep hand OUT of green box", 
                           (self.roi_left, self.roi_top - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                
                # Feed background subtractor
                _ = self.bg_subtractor.apply(roi, learningRate=0.5)
                frame_count += 1
                
                cv2.imshow('Finger Detector (OpenCV)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue
            
            # Detect skin in ROI
            skin_mask = self.detect_skin(roi)
            
            # Show skin mask in a small window for debugging
            cv2.imshow('Skin Detection (Debug)', skin_mask)
            
            # Find contours
            contours, _ = cv2.findContours(skin_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            finger_count = 0
            
            if contours:
                # Get the largest contour (assumed to be the hand)
                max_contour = max(contours, key=cv2.contourArea)
                contour_area = cv2.contourArea(max_contour)
                
                # Show contour area for debugging
                cv2.putText(frame, f"Contour Area: {contour_area:.0f}", 
                           (self.roi_left, self.roi_top - 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Filter small contours (lowered threshold)
                if contour_area > 3000:
                    # Create a drawing canvas
                    drawing = np.zeros_like(roi)
                    
                    # Draw contour
                    cv2.drawContours(drawing, [max_contour], -1, (0, 255, 0), 2)
                    
                    # Count fingers
                    finger_count, drawing = self.count_fingers_contour(max_contour, drawing)
                    
                    # Display the drawing in the ROI area
                    roi_with_drawing = cv2.addWeighted(roi, 0.7, drawing, 0.3, 0)
                    frame[self.roi_top:self.roi_bottom, self.roi_left:self.roi_right] = roi_with_drawing
                    
                    # Perform action
                    action = self.perform_action(finger_count)
                    if action:
                        last_action = action
                else:
                    cv2.putText(frame, "Area too small - move hand closer", 
                               (self.roi_left, self.roi_top - 40),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 2)
            else:
                cv2.putText(frame, "No skin detected - check lighting", 
                           (self.roi_left, self.roi_top - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Draw info panel
            self.draw_info_panel(frame, finger_count, last_action)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit | Place hand in green box", 
                       (10, frame_height - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Show the frame
            cv2.imshow('Finger Detector (OpenCV)', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\nFinger Detector stopped.")

if __name__ == "__main__":
    detector = FingerDetectorOpenCV()
    detector.run()

