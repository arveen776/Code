# Eye Tracker 👁️

A real-time eye tracking application using computer vision that tracks your eye movements through your computer's camera.

## Features

- **Real-time Eye Detection**: Detects and tracks both eyes using your webcam
- **Iris Tracking**: Precisely tracks the position of your iris within each eye
- **Gaze Direction**: Determines where you're looking (up, down, left, right, center)
- **Visual Feedback**: 
  - Eye bounding boxes showing detected eye regions
  - Iris position markers
  - Gaze direction lines
  - Real-time gaze indicator display
- **Coordinate Display**: Shows normalized X/Y coordinates of your gaze (-1 to 1 range)

## How It Works

The application uses:
- **OpenCV**: For camera access and image processing
- **MediaPipe Face Mesh**: Google's machine learning solution for facial landmark detection
- **Iris Landmarks**: Tracks 478 facial landmarks including detailed iris positions

The system:
1. Captures video from your webcam
2. Detects your face and facial landmarks
3. Identifies eye regions and iris positions
4. Calculates gaze direction based on iris position relative to eye boundaries
5. Displays real-time visual feedback

## Requirements

- Python 3.7 or higher
- A working webcam
- Windows/Mac/Linux

## Installation

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **That's it!** You're ready to run the eye tracker.

## Usage

Run the eye tracker with:

```bash
python eye_tracker.py
```

### Controls
- **Press 'q'**: Quit the application

### What You'll See

- **Green circles**: Eye centers
- **Colored circles** (blue/red): Iris positions
- **Lines**: Connecting eye center to iris (shows gaze direction vector)
- **Gray boxes**: Eye bounding regions
- **Top-right indicator**: Gaze direction visualizer showing where you're looking
- **Text overlay**: 
  - Current gaze direction (e.g., "Looking: Left", "Looking: Up Right")
  - X/Y coordinates of your gaze

## Understanding the Output

### Gaze Coordinates
- **X-axis**: -1 (far left) to +1 (far right)
- **Y-axis**: -1 (up) to +1 (down)
- **Center**: Both values near 0

### Gaze Directions
The system detects 9 possible gaze directions:
- Center
- Up, Down, Left, Right
- Up Left, Up Right, Down Left, Down Right

## Troubleshooting

### Camera not detected
- Make sure your webcam is connected and not being used by another application
- Check camera permissions in your system settings

### Poor detection quality
- Ensure good lighting conditions
- Position your face clearly in front of the camera
- Avoid backlighting (light source behind you)

### Application runs slowly
- Close other applications using the camera
- Reduce camera resolution if possible
- Ensure you have a decent CPU (MediaPipe is computationally intensive)

## Technical Details

### Eye Landmark Indices
- **Left Eye**: Landmarks [362, 385, 387, 263, 373, 380]
- **Right Eye**: Landmarks [33, 160, 158, 133, 153, 144]
- **Left Iris**: Landmarks [474, 475, 476, 477]
- **Right Iris**: Landmarks [469, 470, 471, 472]

### Gaze Calculation
The gaze direction is calculated by:
1. Finding the center point of the eye region
2. Finding the center point of the iris
3. Calculating the relative position of the iris within the eye boundaries
4. Normalizing to a -1 to +1 coordinate system

## Potential Applications

- **Accessibility**: Control interfaces with eye movements
- **User Experience Research**: Understand where users look
- **Gaming**: Eye-controlled game mechanics
- **Health Monitoring**: Track eye fatigue or attention
- **AR/VR Development**: Natural gaze-based interactions

## Limitations

- Accuracy depends on lighting conditions and camera quality
- Works best when face is directly facing the camera
- May struggle with glasses (especially reflective ones)
- Not medical-grade; for professional applications, use specialized hardware

## Future Enhancements

Possible improvements:
- Add calibration for improved accuracy
- Record and analyze gaze patterns over time
- Export gaze data for analysis
- Add heatmap visualization
- Support for multiple faces
- Integration with screen coordinates

## License

This project is open source and available for educational and personal use.

## Credits

Built with:
- OpenCV (https://opencv.org/)
- MediaPipe by Google (https://mediapipe.dev/)
- NumPy (https://numpy.org/)

---

**Enjoy tracking your eyes! 👀**


