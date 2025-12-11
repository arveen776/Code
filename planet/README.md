# Neutron Star Collision Simulation

An interactive simulation of binary neutron star mergers with fully adjustable parameters. This simulation allows you to explore how different initial conditions affect the collision dynamics, gravitational wave signals, and orbital evolution.

## Features

- **Interactive Parameter Controls**: Adjust masses, separation, orbital eccentricity, inclination, and phase
- **Real-time Visualization**: 3D trajectory plots, 2D projections, and time-series analysis
- **Physical Quantities Tracked**:
  - Orbital separation over time
  - Total energy (kinetic + potential)
  - Gravitational wave strain (simplified quadrupole approximation)
- **Realistic Neutron Star Properties**: Mass-radius relationships and density calculations

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

Note: `tkinter` is usually included with Python, but if you encounter issues on Linux, install it with:
```bash
sudo apt-get install python3-tk
```

## Usage

Run the simulation:
```bash
python neutron_star_simulation.py
```

### Controls

- **Mass 1 (M☉)**: Mass of the first neutron star in solar masses (0.5 - 3.0)
- **Mass 2 (M☉)**: Mass of the second neutron star in solar masses (0.5 - 3.0)
- **Separation (km)**: Initial separation between the stars (20 - 500 km)
- **Eccentricity**: Orbital eccentricity (0 = circular, 0.9 = highly elliptical)
- **Inclination (°)**: Angle of the orbital plane (0-90°)
- **Phase (°)**: Initial orbital phase (0-360°)
- **Time Step (ms)**: Simulation time step (0.1 - 10 ms)

### Buttons

- **Reset**: Restart the simulation with current parameter values
- **Run/Stop**: Start or stop the animation

## Physics Notes

This simulation uses:

1. **Newtonian Gravity**: The gravitational forces are calculated using Newton's law of universal gravitation. For extremely close encounters, general relativistic effects become important, but this simplified model captures the essential orbital dynamics.

2. **Neutron Star Properties**:
   - Typical mass: ~1.4 solar masses
   - Typical radius: ~10 km
   - Extreme density: ~10¹⁸ kg/m³

3. **Gravitational Waves**: The gravitational wave strain is calculated using a simplified quadrupole formula. Real neutron star mergers produce detectable gravitational waves (as observed by LIGO/Virgo).

4. **Orbital Dynamics**: The simulation calculates circular or elliptical orbits based on the initial conditions. As the stars spiral inward due to gravitational wave emission (approximated), they eventually merge.

## What to Observe

- **Orbital Decay**: Watch how the separation decreases over time
- **Energy Conservation**: The total energy should remain approximately constant (small numerical errors may accumulate)
- **Gravitational Wave Signal**: The strain increases as the stars approach each other
- **Collision**: When the separation becomes less than the sum of the neutron star radii, they merge

## Limitations

This is a simplified educational simulation. Full neutron star merger simulations require:
- General relativistic hydrodynamics
- Equation of state for neutron star matter
- Magnetohydrodynamics
- Nuclear physics for r-process nucleosynthesis
- Massive computational resources

For research-grade simulations, see codes like:
- GR-Athena++
- AREPO
- SPHINCS_BSSN
- Nmesh

## References

- LIGO/Virgo gravitational wave detections (GW170817)
- Binary neutron star merger observations
- Numerical relativity simulations

## License

This is an educational simulation tool. Feel free to modify and experiment!

