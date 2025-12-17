# Autonomous Cube Assembly Simulation

A 3D physics simulation where autonomous cubes self-assemble into predefined shapes under realistic gravity and physics constraints.

## Features

- **Realistic Physics**: Uses Cannon.js physics engine with gravity, collisions, friction, and damping
- **Autonomous Movement**: Cubes move independently toward target positions using force-based control
- **Multiple Shapes**: Predefined shapes including cube, pyramid, wall, tower, L-shape, and stairs
- **Real-time Visualization**: Beautiful 3D rendering with Three.js, shadows, and lighting
- **Self-Assembly Algorithm**: Cubes automatically navigate and stack to form target geometries

## How It Works

1. **Physics Simulation**: Each cube is a rigid body with mass, affected by gravity and collisions
2. **Target Assignment**: Target positions are calculated based on the selected shape template
3. **Autonomous Navigation**: Cubes apply forces toward their target positions:
   - Horizontal attraction forces guide cubes to their X/Z positions
   - Upward forces help cubes climb to their target Y positions
   - Damping prevents excessive oscillation
4. **Assembly Detection**: When a cube is within threshold distance of its target, it's considered "assembled"
5. **Stability**: Assembled cubes have increased damping to maintain position

## Running the Simulation

### Option 1: Using npm (Recommended)

```bash
npm install
npm start
```

Then open `http://localhost:8080` in your browser.

### Option 2: Using Python

```bash
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

### Option 3: Using any HTTP server

Serve the files using any static file server and open `index.html`.

## Controls

- **Target Shape**: Select from predefined shapes (cube, pyramid, wall, tower, L-shape, stairs)
- **Number of Cubes**: Choose how many cubes to spawn (10-50)
- **Start Assembly**: Begin the self-assembly process
- **Reset**: Clear all cubes and reset the simulation
- **Arrow Keys**: Adjust camera view (Left/Right to rotate, Up/Down to change height)

## Physics Parameters

The simulation uses realistic physics parameters:

- **Gravity**: -9.82 m/s² (Earth gravity)
- **Cube Size**: 0.5 units
- **Cube Mass**: 1 kg
- **Friction**: 0.4
- **Restitution**: 0.3 (bounciness)
- **Damping**: 0.4 (air resistance)
- **Movement Force**: 50 N (horizontal movement)
- **Attraction Force**: 30 N (toward target)
- **Assembly Threshold**: 0.15 units (distance to consider assembled)

## Technical Details

- **Rendering**: Three.js for 3D graphics
- **Physics**: Cannon.js (cannon-es) for rigid body dynamics
- **Algorithm**: Force-based autonomous navigation with target attraction
- **Collision Detection**: Broadphase + narrowphase collision detection
- **Performance**: Optimized for 20-50 cubes with 60 FPS physics updates

## Customization

You can modify the physics parameters in `simulation.js`:

```javascript
const CUBE_SIZE = 0.5;        // Size of each cube
const CUBE_MASS = 1;          // Mass of each cube
const GRAVITY = -9.82;        // Gravity strength
const MOVEMENT_FORCE = 50;    // Maximum movement force
const ATTRACTION_FORCE = 30;  // Force toward target
const DAMPING = 0.4;          // Linear/angular damping
const ASSEMBLY_THRESHOLD = 0.15; // Distance for assembly
```

## Adding New Shapes

To add a new shape, add an entry to `SHAPE_TEMPLATES` in `simulation.js`:

```javascript
'my-shape': {
    name: 'My Custom Shape',
    positions: [
        { x: 0, y: 0.25, z: 0 },
        { x: 0.5, y: 0.25, z: 0 },
        // ... more positions
    ]
}
```

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (may need to enable ES6 modules)

## License

MIT

