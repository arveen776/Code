# Finger Mouse Controller

A Python application that tracks your finger/object movement via webcam and translates it to mouse cursor movement, allowing you to control your mouse without touching it.

## Features

- Real-time tracking using OpenCV (compatible with Python 3.13+)
- Two tracking modes: Motion detection and Color-based tracking
- Smooth mouse cursor movement with configurable sensitivity
- Visual feedback with tracking indicators
- Easy calibration for color tracking
- Works with any Python version - no MediaPipe required!

## Installation

1. Install Python 3.7 or higher (tested with Python 3.13)

2. Install required packages:
```bash
pip install -r requirements.txt
```

All packages are compatible with Python 3.13!

## Usage

1. Run the application:
```bash
python finger_mouse.py
```

2. Position yourself in front of your webcam
3. By default, it uses **motion tracking** - just hold your finger/object in front of the camera and move it
4. The mouse cursor will follow your finger/object movement

## Tracking Modes

### Motion Tracking (Default)
- No setup required - just hold your finger/object in front of the camera
- Tracks any moving object
- Best for quick testing and general use

### Color Tracking
- Tracks a specific colored object (works great with colored markers/tape on your finger)
- Press 'c' to calibrate - hold the colored object in the center of the frame for 3 seconds
- More precise and stable tracking

Press 'm' to toggle between motion and color tracking modes.

## Controls

- **Move finger/object**: Control mouse cursor movement
- **Press 'q'**: Quit the application
- **Press 'r'**: Reset mouse position to center of screen
- **Press 'c'**: Calibrate color tracking (detects object in center of frame)
- **Press 'm'**: Toggle between motion and color tracking modes

## Configuration

You can adjust the following parameters in `finger_mouse.py`:

- `SMOOTHING`: Controls movement smoothing (0-1), higher = smoother movement (default: 0.7)
- `MOVEMENT_SCALE`: Controls movement sensitivity, higher = more sensitive (default: 2.0)
- Camera resolution: Adjust in the `__init__` method
- Color bounds: Adjust `lower_bound` and `upper_bound` for color tracking

## Troubleshooting

- **Camera not detected**: Make sure your webcam is connected and not being used by another application
- **Mouse too sensitive**: Decrease `MOVEMENT_SCALE` or increase `SMOOTHING` in the code
- **Mouse not moving**: 
  - For motion tracking: Ensure your finger/object is clearly visible and moving
  - For color tracking: Make sure the colored object is well-lit and press 'c' to recalibrate
- **Tracking is jumpy**: Try increasing `SMOOTHING` value or using color tracking mode with a colored marker

## Tips for Best Results

- Use good lighting conditions
- For motion tracking: Stay still at first to let the background calibrate, then move your finger
- For color tracking: Use a bright, distinct color (like orange, yellow, or green tape/marker) on your finger tip
- Position yourself 1-2 feet away from the camera for best results

## Notes

- Requires a webcam/camera
- Works with Python 3.13+ (no compatibility issues!)
- Motion tracking mode requires the camera view to be relatively stable (minimal background movement)

