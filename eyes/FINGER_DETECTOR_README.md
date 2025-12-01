# Finger Detector 🖐️

A real-time finger counting and gesture recognition application using computer vision that detects hand gestures through your computer's camera and triggers actions based on finger count.

## Features

- **Real-time Hand Detection**: Detects hands using your webcam
- **Finger Counting**: Accurately counts the number of raised fingers (0-5)
- **Gesture Recognition**: Recognizes gestures from fist (0 fingers) to open palm (5 fingers)
- **Action Triggers**: Performs different actions based on finger count
- **Visual Feedback**: 
  - Hand skeleton/contour visualization
  - Color-coded backgrounds for each gesture
  - Real-time finger count display
  - Action labels
- **Multi-hand Support**: MediaPipe version supports detecting both hands simultaneously

## How It Works

### MediaPipe Version (`finger_detector.py`)
The application uses:
- **MediaPipe Hands**: Google's machine learning solution for hand landmark detection
- Tracks 21 hand landmarks per hand
- Analyzes finger positions to determine if each finger is raised or lowered
- More accurate and works without specific positioning

### OpenCV Version (`finger_detector_opencv.py`)
Uses traditional computer vision techniques:
- **Skin color detection**: Identifies hand region using HSV color space
- **Contour analysis**: Finds hand contours
- **Convexity defects**: Counts fingers by analyzing the gaps between fingers
- Requires hand to be placed in a specific region (green box)

## Gesture Actions

The system recognizes 6 different gestures:

| Fingers | Gesture | Action |
|---------|---------|--------|
| 0 | ✊ Fist | No action |
| 1 | ☝️ One Finger | Play/Pause |
| 2 | ✌️ Two Fingers | Volume Up |
| 3 | 🤟 Three Fingers | Volume Down |
| 4 | 🖖 Four Fingers | Next Track |
| 5 | 🖐️ Open Palm | Previous Track |

**Note**: These are example actions. You can customize them by modifying the `perform_action()` method in the code!

## Requirements

- Python 3.7+ (MediaPipe version requires Python 3.11 or 3.12)
- Python 3.13 works with OpenCV-only version
- A working webcam
- Windows/Mac/Linux

## Installation

### For OpenCV Version (Python 3.13 compatible):
```bash
pip install opencv-python numpy
```

### For MediaPipe Version (Python 3.11/3.12 only):
```bash
pip install opencv-python mediapipe numpy
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Usage

### Run the OpenCV Version (Recommended for Python 3.13):
```bash
python finger_detector_opencv.py
```

**Instructions:**
1. Keep your hand OUT of the green box during calibration (first 30 frames)
2. After calibration, place your hand inside the green rectangle
3. Spread your fingers wide for best detection
4. Try different finger combinations

### Run the MediaPipe Version (More Accurate):
```bash
python finger_detector.py
```

**Instructions:**
1. Show your hand(s) anywhere in the frame
2. No calibration needed
3. Works with multiple hands
4. Try different finger combinations

### Controls
- **Press 'q'**: Quit the application

## What You'll See

### MediaPipe Version:
- Hand skeleton with landmarks and connections
- Green circles at fingertips (finger is up)
- Red circles at fingertips (finger is down)
- Hand type label (Left/Right)
- Colored background changing with gesture
- Finger count and action text

### OpenCV Version:
- Green rectangle (region of interest)
- Hand contour in green
- Red dots at finger valleys (gaps)
- Blue dot at hand center
- Colored background changing with gesture
- Finger count and action text

## Customizing Actions

You can easily customize what happens for each gesture by modifying the `perform_action()` method:

```python
def perform_action(self, finger_count):
    actions = {
        0: "Your custom action for fist",
        1: "Your custom action for 1 finger",
        2: "Your custom action for 2 fingers",
        3: "Your custom action for 3 fingers",
        4: "Your custom action for 4 fingers",
        5: "Your custom action for 5 fingers"
    }
    
    # Add your custom code here!
    # Examples:
    # - Control media playback (pyautogui, keyboard library)
    # - Send commands to smart home devices
    # - Control games or applications
    # - Trigger automation scripts
    
    return actions.get(finger_count, "Unknown")
```

## Advanced Usage Examples

### 1. Control Media Playback
Install `keyboard` library: `pip install keyboard`

```python
import keyboard

def perform_action(self, finger_count):
    if finger_count == 1:
        keyboard.press_and_release('space')  # Play/Pause
    elif finger_count == 2:
        keyboard.press_and_release('volume up')
    elif finger_count == 3:
        keyboard.press_and_release('volume down')
    # ... etc
```

### 2. Control Mouse
Install `pyautogui` library: `pip install pyautogui`

```python
import pyautogui

def perform_action(self, finger_count):
    if finger_count == 1:
        pyautogui.click()  # Click
    elif finger_count == 2:
        pyautogui.scroll(10)  # Scroll up
    # ... etc
```

### 3. Send HTTP Requests (Control IoT devices)
```python
import requests

def perform_action(self, finger_count):
    if finger_count == 5:
        # Turn on smart lights
        requests.post('http://your-device-ip/api/lights/on')
```

## Troubleshooting

### Camera not detected
- Make sure your webcam is connected
- Check camera permissions in system settings
- Close other applications using the camera

### Poor finger detection (OpenCV version)
- Ensure good lighting conditions
- Keep hand inside the green rectangle
- Spread fingers wide apart
- Adjust lighting to avoid shadows
- Try adjusting the `lower_skin` and `upper_skin` values in `detect_skin()` method

### Fingers not counting correctly
- **OpenCV**: Make sure fingers are spread wide with clear gaps between them
- **MediaPipe**: Works better with natural hand poses
- Keep hand flat and facing the camera
- Avoid cluttered backgrounds

### Actions triggering too frequently
- Adjust the `action_cooldown` value (default: 1.0 second)
- Increase it for less frequent triggers

### MediaPipe installation fails
- Ensure you're using Python 3.11 or 3.12 (not 3.13)
- Use the OpenCV version as an alternative

## Comparison: MediaPipe vs OpenCV

| Feature | MediaPipe Version | OpenCV Version |
|---------|------------------|----------------|
| Accuracy | ⭐⭐⭐⭐⭐ Very High | ⭐⭐⭐ Moderate |
| Speed | ⭐⭐⭐⭐ Fast | ⭐⭐⭐⭐⭐ Very Fast |
| Setup | Requires specific Python version | Works with any Python |
| Ease of Use | Easy - works anywhere | Requires ROI positioning |
| Multi-hand | ✅ Yes | ❌ No |
| Lighting Sensitivity | Low | High |
| Python 3.13 Support | ❌ No | ✅ Yes |

## Technical Details

### MediaPipe Finger Detection
Uses landmark positions:
- **Thumb**: Checks if tip (landmark 4) is to the right/left of base (landmark 2)
- **Other Fingers**: Checks if tip (landmarks 8, 12, 16, 20) is above base (landmarks 6, 10, 14, 18)

### OpenCV Finger Detection
Uses convexity defects:
1. Detect skin color in HSV space
2. Find hand contour
3. Calculate convex hull
4. Analyze convexity defects (gaps between fingers)
5. Count defects with suitable angles and distances

## Potential Applications

- **Touchless Control**: Control presentations, media players, or applications
- **Accessibility**: Help users with limited mobility control devices
- **Gaming**: Create gesture-based game controls
- **Smart Home**: Control IoT devices with hand gestures
- **Virtual Meetings**: Gesture-based reactions or controls
- **Education**: Interactive learning applications
- **Art Installation**: Create interactive art pieces

## Limitations

- Lighting conditions affect accuracy (especially OpenCV version)
- Background clutter can interfere with detection
- Works best with clear hand visibility
- OpenCV version requires specific hand positioning
- MediaPipe requires Python 3.11/3.12

## Future Enhancements

Possible improvements:
- Add more complex gestures (thumbs up, peace sign, etc.)
- Implement gesture sequences (combos)
- Add recording and playback of gesture patterns
- Create gesture macro system
- Add voice feedback
- Support for custom gesture training
- Integration with popular applications (Spotify, VLC, etc.)

## Credits

Built with:
- OpenCV (https://opencv.org/)
- MediaPipe by Google (https://mediapipe.dev/)
- NumPy (https://numpy.org/)

---

**Control your computer with your hands! 🖐️✨**


