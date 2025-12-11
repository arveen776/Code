# Gravity Simulation GUI

A modular gravity simulation application that visualizes gravitational interactions between bodies and particles.

## Features

- **Modular Parameter System**: Easy to add new parameters by creating files in the `parameters/` folder
- **Interactive GUI**: Place bodies and particles, adjust parameters in real-time
- **Trajectory Visualization**: See particle paths as they orbit or fall toward massive bodies
- **Real-time Simulation**: Adjustable simulation speed with play/pause controls

## How to Run

```bash
python gravity_gui.py
```

## Usage

1. **Adjust Mass Parameter**: Use the mass slider to set the gravitational body's mass
2. **Place a Body**: Click "Place Body at Center" to create a gravitational body at the center of the canvas
3. **Place Particles**: 
   - Click "Place Particle (Click Canvas)" button
   - Click anywhere on the canvas to place a particle
   - Watch it move under the influence of gravity!
4. **Control Simulation**: Use play/pause and speed controls to manage the simulation

## Adding New Parameters

To add a new parameter, simply create a new file in the `parameters/` folder following this pattern:

```python
# parameters/your_parameter.py
class YourParameter:
    def __init__(self, value=default_value, unit="unit"):
        self.value = value
        self.unit = unit
    
    def get_value(self):
        return self.value
    
    def set_value(self, value):
        self.value = value
    
    def get_display_name(self):
        return "Your Parameter Name"
    
    def get_unit(self):
        return self.unit
```

Then:
1. Import it in `parameters/__init__.py`
2. Add it to the GUI in `gravity_gui.py` (in `setup_ui` method)
3. Use it in your physics calculations

## Current Parameters

- **Mass**: Controls the mass of gravitational bodies (100-10000 kg)

## Project Structure

```
.
├── gravity_gui.py          # Main GUI application
├── physics_engine.py       # Physics simulation engine
├── parameters/             # Modular parameter system
│   ├── __init__.py
│   └── mass.py            # Mass parameter
└── README.md
```

