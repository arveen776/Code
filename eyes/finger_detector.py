import cv2
import mediapipe as mp
import numpy as np
import time

class FingerDetector:
    def __init__(self):
        # Initialize MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Finger tip and base landmark IDs
        self.finger_tips = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        self.finger_bases = [2, 6, 10, 14, 18]
        
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
        
    def count_fingers(self, hand_landmarks, handedness):
        """Count the number of raised fingers"""
        if not hand_landmarks:
            return 0
        
        fingers_up = []
        
        # Check if it's left or right hand
        is_right_hand = handedness == "Right"
        
        # Thumb (special case - check horizontal position)
        thumb_tip = hand_landmarks.landmark[self.finger_tips[0]]
        thumb_base = hand_landmarks.landmark[self.finger_bases[0]]
        
        if is_right_hand:
            # Right hand: thumb is up if tip is to the right of base
            fingers_up.append(thumb_tip.x > thumb_base.x)
        else:
            # Left hand: thumb is up if tip is to the left of base
            fingers_up.append(thumb_tip.x < thumb_base.x)
        
        # Other four fingers (check vertical position)
        for i in range(1, 5):
            tip = hand_landmarks.landmark[self.finger_tips[i]]
            base = hand_landmarks.landmark[self.finger_bases[i]]
            # Finger is up if tip is above base (lower y value)
            fingers_up.append(tip.y < base.y)
        
        return sum(fingers_up)
    
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
    
    def draw_info_panel(self, frame, finger_count, action_text, hand_count):
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
        
        # Display hand count
        hand_text = f"Hands: {hand_count}"
        cv2.putText(frame, hand_text, (w - 180, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    def draw_finger_indicators(self, frame, hand_landmarks, finger_count):
        """Draw visual indicators for each finger"""
        if not hand_landmarks:
            return
        
        h, w = frame.shape[:2]
        
        # Draw circles at fingertips
        colors = [(0, 255, 0), (0, 200, 0), (0, 150, 0), (0, 100, 0), (0, 50, 0)]
        
        for i, tip_id in enumerate(self.finger_tips):
            landmark = hand_landmarks.landmark[tip_id]
            x, y = int(landmark.x * w), int(landmark.y * h)
            
            # Determine if finger is up
            is_up = i < finger_count
            color = (0, 255, 0) if is_up else (0, 0, 255)
            
            cv2.circle(frame, (x, y), 15, color, -1)
            cv2.circle(frame, (x, y), 15, (255, 255, 255), 2)
    
    def run(self):
        """Main loop to run finger detection"""
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Finger Detector Started! (MediaPipe Version)")
        print("Show your hand(s) to the camera")
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
        
        last_action = None
        
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
            results = self.hands.process(rgb_frame)
            
            frame_height, frame_width = frame.shape[:2]
            total_fingers = 0
            hand_count = 0
            
            if results.multi_hand_landmarks and results.multi_handedness:
                hand_count = len(results.multi_hand_landmarks)
                
                for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                    # Draw hand landmarks
                    self.mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # Count fingers
                    hand_type = handedness.classification[0].label
                    finger_count = self.count_fingers(hand_landmarks, hand_type)
                    total_fingers += finger_count
                    
                    # Draw finger indicators
                    self.draw_finger_indicators(frame, hand_landmarks, finger_count)
                    
                    # Display hand type
                    wrist = hand_landmarks.landmark[0]
                    wrist_x, wrist_y = int(wrist.x * frame_width), int(wrist.y * frame_height)
                    cv2.putText(frame, f"{hand_type} ({finger_count})", 
                               (wrist_x - 50, wrist_y - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                
                # Perform action based on total finger count
                action = self.perform_action(total_fingers)
                if action:
                    last_action = action
            else:
                # Reset background when no hands detected
                self.bg_color = (50, 50, 50)
            
            # Draw info panel
            self.draw_info_panel(frame, total_fingers, last_action, hand_count)
            
            # Display instructions
            cv2.putText(frame, "Press 'q' to quit", (10, frame_height - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
            
            # Show the frame
            cv2.imshow('Finger Detector', frame)
            
            # Exit on 'q' press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        print("\nFinger Detector stopped.")

if __name__ == "__main__":
    detector = FingerDetector()
    detector.run()

