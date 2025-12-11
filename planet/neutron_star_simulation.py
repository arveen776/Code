"""
Neutron Star Collision Simulation
A simplified but physically meaningful simulation of binary neutron star mergers
with interactive parameter controls.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
import scipy.constants as const
from dataclasses import dataclass
from typing import Tuple, List
import math


@dataclass
class NeutronStar:
    """Represents a neutron star with physical properties"""
    mass: float  # Solar masses
    radius: float  # km
    position: np.ndarray  # 3D position vector (km)
    velocity: np.ndarray  # 3D velocity vector (km/s)
    spin: float = 0.0  # Angular velocity (rad/s)
    
    @property
    def mass_kg(self) -> float:
        """Mass in kilograms"""
        return self.mass * 1.989e30  # Solar mass in kg
    
    @property
    def density(self) -> float:
        """Average density in kg/m³"""
        volume = (4/3) * np.pi * (self.radius * 1000)**3  # Convert km to m
        return self.mass_kg / volume
    
    @property
    def schwarzschild_radius(self) -> float:
        """Schwarzschild radius in km"""
        return 2 * const.G * self.mass_kg / (const.c**2) / 1000  # Convert to km


class NeutronStarSimulator:
    """Main simulation engine for neutron star collisions"""
    
    def __init__(self):
        # Physical constants
        self.G = const.G  # Gravitational constant (m³/kg/s²)
        self.c = const.c  # Speed of light (m/s)
        self.solar_mass = 1.989e30  # kg
        self.km_to_m = 1000
        
        # Simulation parameters
        self.dt = 0.001  # Time step (seconds)
        self.time = 0.0
        self.stars: List[NeutronStar] = []
        self.trajectory_history: List[List[np.ndarray]] = []
        self.energy_history: List[float] = []
        self.separation_history: List[float] = []
        self.gw_strain_history: List[float] = []
        
        # Default parameters
        self.default_mass1 = 1.4  # Solar masses
        self.default_mass2 = 1.4
        self.default_separation = 100.0  # km
        self.default_orbital_velocity = 0.0  # km/s (0 = circular orbit calculated)
        self.default_eccentricity = 0.0
        
    def create_binary_system(self, 
                            mass1: float = 1.4,
                            mass2: float = 1.4,
                            separation: float = 100.0,
                            eccentricity: float = 0.0,
                            inclination: float = 0.0,
                            phase: float = 0.0):
        """
        Create a binary neutron star system
        
        Parameters:
        -----------
        mass1, mass2 : float
            Masses in solar masses
        separation : float
            Initial separation in km
        eccentricity : float
            Orbital eccentricity (0 = circular, 1 = parabolic)
        inclination : float
            Orbital plane inclination in degrees
        phase : float
            Initial orbital phase in degrees
        """
        # Calculate neutron star radii (approximate: R ~ 10km for 1.4 M_sun)
        radius1 = 10.0 * (mass1 / 1.4)**(1/3)  # Rough scaling
        radius2 = 10.0 * (mass2 / 1.4)**(1/3)
        
        # Total mass
        M_total = (mass1 + mass2) * self.solar_mass
        separation_m = separation * self.km_to_m
        
        # Calculate orbital parameters
        if eccentricity == 0:
            # Circular orbit
            v_circular = np.sqrt(self.G * M_total / separation_m) / self.km_to_m  # km/s
            v1 = v_circular * mass2 / (mass1 + mass2)
            v2 = v_circular * mass1 / (mass1 + mass2)
        else:
            # Elliptical orbit (simplified)
            a = separation / (1 - eccentricity)  # Semi-major axis
            v1 = np.sqrt(self.G * M_total * (2/separation_m - 1/(a*self.km_to_m))) * mass2 / (mass1 + mass2) / self.km_to_m
            v2 = np.sqrt(self.G * M_total * (2/separation_m - 1/(a*self.km_to_m))) * mass1 / (mass1 + mass2) / self.km_to_m
        
        # Convert angles to radians
        phase_rad = np.deg2rad(phase)
        inc_rad = np.deg2rad(inclination)
        
        # Position star 1 at origin, star 2 at separation
        pos1 = np.array([0.0, 0.0, 0.0])
        pos2 = np.array([separation * np.cos(phase_rad), 
                         separation * np.sin(phase_rad) * np.cos(inc_rad),
                         separation * np.sin(phase_rad) * np.sin(inc_rad)])
        
        # Velocities perpendicular to separation
        v_dir = np.array([-np.sin(phase_rad), 
                          np.cos(phase_rad) * np.cos(inc_rad),
                          np.cos(phase_rad) * np.sin(inc_rad)])
        
        vel1 = v1 * v_dir
        vel2 = -v2 * v_dir
        
        # Create neutron stars
        self.stars = [
            NeutronStar(mass1, radius1, pos1, vel1),
            NeutronStar(mass2, radius2, pos2, vel2)
        ]
        
        # Reset history
        self.time = 0.0
        self.trajectory_history = [[], []]
        self.energy_history = []
        self.separation_history = []
        self.gw_strain_history = []
        
    def calculate_gravitational_force(self, star1: NeutronStar, star2: NeutronStar) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate gravitational force between two stars
        Returns forces on star1 and star2
        """
        r_vec = star2.position - star1.position
        r = np.linalg.norm(r_vec)
        
        if r < 1e-6:  # Avoid division by zero
            return np.zeros(3), np.zeros(3)
        
        # Newtonian gravity
        F_mag = self.G * star1.mass_kg * star2.mass_kg / (r * self.km_to_m)**2
        F_dir = r_vec / r
        F1 = F_mag * F_dir / self.km_to_m  # Convert to km/s² units
        F2 = -F1
        
        return F1, F2
    
    def calculate_energy(self) -> float:
        """Calculate total energy (kinetic + potential)"""
        if len(self.stars) != 2:
            return 0.0
        
        # Kinetic energy
        KE = 0.5 * self.stars[0].mass_kg * np.linalg.norm(self.stars[0].velocity * self.km_to_m)**2
        KE += 0.5 * self.stars[1].mass_kg * np.linalg.norm(self.stars[1].velocity * self.km_to_m)**2
        
        # Potential energy
        r = np.linalg.norm(self.stars[1].position - self.stars[0].position)
        PE = -self.G * self.stars[0].mass_kg * self.stars[1].mass_kg / (r * self.km_to_m)
        
        return KE + PE
    
    def calculate_gravitational_wave_strain(self) -> float:
        """
        Simplified gravitational wave strain calculation
        Uses quadrupole formula approximation
        """
        if len(self.stars) != 2:
            return 0.0
        
        # Reduced mass
        mu = (self.stars[0].mass_kg * self.stars[1].mass_kg) / (self.stars[0].mass_kg + self.stars[1].mass_kg)
        
        # Separation and relative velocity
        r_vec = self.stars[1].position - self.stars[0].position
        r = np.linalg.norm(r_vec) * self.km_to_m  # Convert to meters
        v_vec = self.stars[1].velocity - self.stars[0].velocity
        v = np.linalg.norm(v_vec) * self.km_to_m  # Convert to m/s
        
        if r < 1e-6:
            return 0.0
        
        # Orbital frequency
        omega = v / r
        
        # Quadrupole moment (simplified)
        # h ~ (G/c^4) * (mu * omega^2 * r^2) / distance
        # For visualization, we'll use a simplified form
        distance = 100e6 * const.parsec  # Assume 100 Mpc distance
        h = (4 * self.G * mu * omega**2 * r**2) / (self.c**4 * distance)
        
        return abs(h) * 1e21  # Scale for visualization
    
    def calculate_gw_energy_loss(self) -> float:
        """
        Calculate energy loss rate due to gravitational wave emission
        Uses quadrupole formula: dE/dt = (32/5) * (G^4/c^5) * (mu^2 * M^3) / r^5
        """
        if len(self.stars) != 2:
            return 0.0
        
        mu = (self.stars[0].mass_kg * self.stars[1].mass_kg) / (self.stars[0].mass_kg + self.stars[1].mass_kg)
        M_total = self.stars[0].mass_kg + self.stars[1].mass_kg
        r = np.linalg.norm(self.stars[1].position - self.stars[0].position) * self.km_to_m
        
        if r < 1e-6:
            return 0.0
        
        # Energy loss rate (Watts)
        dE_dt = (32.0 / 5.0) * (self.G**4 / self.c**5) * (mu**2 * M_total**3) / r**5
        
        return dE_dt
    
    def step(self):
        """Advance simulation by one time step"""
        if len(self.stars) != 2:
            return
        
        # Calculate forces
        F1, F2 = self.calculate_gravitational_force(self.stars[0], self.stars[1])
        
        # Calculate gravitational wave energy loss
        # This causes orbital decay - we approximate by reducing orbital energy
        dE_dt = self.calculate_gw_energy_loss()
        separation = np.linalg.norm(self.stars[1].position - self.stars[0].position)
        
        # Apply GW energy loss as a small radial acceleration (simplified)
        # This is an approximation - in reality GW emission is more complex
        if separation > (self.stars[0].radius + self.stars[1].radius) * 1.1:
            # Calculate relative velocity
            v_rel = self.stars[1].velocity - self.stars[0].velocity
            v_rel_mag = np.linalg.norm(v_rel) * self.km_to_m  # m/s
            
            if v_rel_mag > 0:
                # Estimate energy loss effect on orbital motion
                # Convert energy loss to velocity change
                total_energy = self.calculate_energy()
                if total_energy < 0:  # Bound orbit
                    # Approximate: reduce orbital energy slightly
                    energy_loss = dE_dt * self.dt
                    # This causes the orbit to shrink
                    # We apply a small radial acceleration toward each other
                    r_vec = self.stars[1].position - self.stars[0].position
                    r_unit = r_vec / separation if separation > 0 else np.zeros(3)
                    
                    # Small additional radial acceleration due to GW emission
                    # This is a simplified model
                    gw_accel_magnitude = energy_loss / (0.5 * (self.stars[0].mass_kg + self.stars[1].mass_kg) * separation * self.km_to_m)
                    gw_accel = -gw_accel_magnitude * r_unit / self.km_to_m  # Convert to km/s²
                    
                    # Distribute acceleration between stars
                    F1 += self.stars[0].mass_kg * gw_accel * (self.stars[1].mass_kg / (self.stars[0].mass_kg + self.stars[1].mass_kg))
                    F2 -= self.stars[1].mass_kg * gw_accel * (self.stars[0].mass_kg / (self.stars[0].mass_kg + self.stars[1].mass_kg))
        
        # Update velocities (using km/s² units)
        self.stars[0].velocity += F1 * self.dt
        self.stars[1].velocity += F2 * self.dt
        
        # Update positions
        self.stars[0].position += self.stars[0].velocity * self.dt
        self.stars[1].position += self.stars[1].velocity * self.dt
        
        # Check for collision (when separation < sum of radii)
        separation = np.linalg.norm(self.stars[1].position - self.stars[0].position)
        if separation < (self.stars[0].radius + self.stars[1].radius):
            # Merge - stop simulation or handle collision
            # For now, we just continue but the stars have merged
            pass
        
        # Record history
        self.trajectory_history[0].append(self.stars[0].position.copy())
        self.trajectory_history[1].append(self.stars[1].position.copy())
        self.energy_history.append(self.calculate_energy())
        self.separation_history.append(separation)
        self.gw_strain_history.append(self.calculate_gravitational_wave_strain())
        
        self.time += self.dt
    
    def run_simulation(self, num_steps: int = 10000):
        """Run simulation for specified number of steps"""
        for _ in range(num_steps):
            self.step()


class SimulationVisualizer:
    """Interactive visualization of neutron star collision"""
    
    def __init__(self, simulator: NeutronStarSimulator):
        self.simulator = simulator
        self.fig = plt.figure(figsize=(16, 10))
        self.setup_plots()
        self.setup_controls()
        self.animation = None
        self.is_running = False
        
    def setup_plots(self):
        """Set up all plot axes"""
        # 3D trajectory plot
        self.ax_3d = self.fig.add_subplot(2, 3, (1, 4), projection='3d')
        self.ax_3d.set_xlabel('X (km)')
        self.ax_3d.set_ylabel('Y (km)')
        self.ax_3d.set_zlabel('Z (km)')
        self.ax_3d.set_title('3D Trajectory')
        
        # XY projection
        self.ax_xy = self.fig.add_subplot(2, 3, 2)
        self.ax_xy.set_xlabel('X (km)')
        self.ax_xy.set_ylabel('Y (km)')
        self.ax_xy.set_title('XY Projection')
        self.ax_xy.grid(True)
        self.ax_xy.set_aspect('equal')
        
        # Separation vs time
        self.ax_sep = self.fig.add_subplot(2, 3, 3)
        self.ax_sep.set_xlabel('Time (s)')
        self.ax_sep.set_ylabel('Separation (km)')
        self.ax_sep.set_title('Separation')
        self.ax_sep.grid(True)
        
        # Energy vs time
        self.ax_energy = self.fig.add_subplot(2, 3, 5)
        self.ax_energy.set_xlabel('Time (s)')
        self.ax_energy.set_ylabel('Total Energy (J)')
        self.ax_energy.set_title('Energy Conservation')
        self.ax_energy.grid(True)
        
        # Gravitational wave strain
        self.ax_gw = self.fig.add_subplot(2, 3, 6)
        self.ax_gw.set_xlabel('Time (s)')
        self.ax_gw.set_ylabel('GW Strain (×10⁻²¹)')
        self.ax_gw.set_title('Gravitational Wave Signal')
        self.ax_gw.grid(True)
        
        plt.tight_layout()
    
    def setup_controls(self):
        """Set up interactive controls"""
        # Create sliders
        slider_y = 0.02
        slider_height = 0.02
        slider_width = 0.15
        
        # Mass 1 slider
        ax_mass1 = plt.axes([0.02, 0.95, slider_width, slider_height])
        self.slider_mass1 = Slider(ax_mass1, 'Mass 1 (M☉)', 0.5, 3.0, 
                                   valinit=self.simulator.default_mass1, valstep=0.1)
        
        # Mass 2 slider
        ax_mass2 = plt.axes([0.02, 0.92, slider_width, slider_height])
        self.slider_mass2 = Slider(ax_mass2, 'Mass 2 (M☉)', 0.5, 3.0, 
                                   valinit=self.simulator.default_mass2, valstep=0.1)
        
        # Separation slider
        ax_sep = plt.axes([0.02, 0.89, slider_width, slider_height])
        self.slider_sep = Slider(ax_sep, 'Separation (km)', 20, 500, 
                                valinit=self.simulator.default_separation, valstep=10)
        
        # Eccentricity slider
        ax_ecc = plt.axes([0.02, 0.86, slider_width, slider_height])
        self.slider_ecc = Slider(ax_ecc, 'Eccentricity', 0.0, 0.9, 
                                valinit=0.0, valstep=0.05)
        
        # Inclination slider
        ax_inc = plt.axes([0.02, 0.83, slider_width, slider_height])
        self.slider_inc = Slider(ax_inc, 'Inclination (°)', 0, 90, 
                                valinit=0, valstep=5)
        
        # Phase slider
        ax_phase = plt.axes([0.02, 0.80, slider_width, slider_height])
        self.slider_phase = Slider(ax_phase, 'Phase (°)', 0, 360, 
                                  valinit=0, valstep=10)
        
        # Time step slider
        ax_dt = plt.axes([0.02, 0.77, slider_width, slider_height])
        self.slider_dt = Slider(ax_dt, 'Time Step (ms)', 0.1, 10, 
                               valinit=self.simulator.dt*1000, valstep=0.1)
        
        # Buttons
        ax_reset = plt.axes([0.02, 0.70, 0.08, 0.03])
        self.button_reset = Button(ax_reset, 'Reset')
        self.button_reset.on_clicked(self.reset_simulation)
        
        ax_run = plt.axes([0.11, 0.70, 0.08, 0.03])
        self.button_run = Button(ax_run, 'Run')
        self.button_run.on_clicked(self.toggle_animation)
        
        # Connect sliders
        self.slider_mass1.on_changed(self.update_parameters)
        self.slider_mass2.on_changed(self.update_parameters)
        self.slider_sep.on_changed(self.update_parameters)
        self.slider_ecc.on_changed(self.update_parameters)
        self.slider_inc.on_changed(self.update_parameters)
        self.slider_phase.on_changed(self.update_parameters)
        self.slider_dt.on_changed(self.update_dt)
    
    def update_dt(self, val):
        """Update time step"""
        self.simulator.dt = self.slider_dt.val / 1000.0
    
    def update_parameters(self, val):
        """Update simulation parameters"""
        if not self.is_running:
            self.reset_simulation(None)
    
    def reset_simulation(self, event):
        """Reset and restart simulation"""
        self.simulator.create_binary_system(
            mass1=self.slider_mass1.val,
            mass2=self.slider_mass2.val,
            separation=self.slider_sep.val,
            eccentricity=self.slider_ecc.val,
            inclination=self.slider_inc.val,
            phase=self.slider_phase.val
        )
        self.update_plots()
    
    def toggle_animation(self, event):
        """Start/stop animation"""
        if self.is_running:
            if self.animation:
                self.animation.event_source.stop()
            self.is_running = False
            self.button_run.label.set_text('Run')
        else:
            self.is_running = True
            self.button_run.label.set_text('Stop')
            self.animation = FuncAnimation(self.fig, self.animate, interval=50, blit=False)
            plt.draw()
    
    def animate(self, frame):
        """Animation frame update"""
        # Run multiple steps per frame for speed
        for _ in range(100):
            self.simulator.step()
        self.update_plots()
        return []
    
    def update_plots(self):
        """Update all plots"""
        # Clear axes
        self.ax_3d.clear()
        self.ax_xy.clear()
        self.ax_sep.clear()
        self.ax_energy.clear()
        self.ax_gw.clear()
        
        if len(self.simulator.trajectory_history[0]) == 0:
            return
        
        # Get current positions
        if len(self.simulator.stars) == 2:
            pos1 = self.simulator.stars[0].position
            pos2 = self.simulator.stars[1].position
            
            # 3D plot
            traj1 = np.array(self.simulator.trajectory_history[0])
            traj2 = np.array(self.simulator.trajectory_history[1])
            
            if len(traj1) > 1:
                self.ax_3d.plot(traj1[:, 0], traj1[:, 1], traj1[:, 2], 'b-', alpha=0.5, linewidth=1)
                self.ax_3d.plot(traj2[:, 0], traj2[:, 1], traj2[:, 2], 'r-', alpha=0.5, linewidth=1)
            
            self.ax_3d.scatter([pos1[0]], [pos1[1]], [pos1[2]], c='blue', s=100, marker='o')
            self.ax_3d.scatter([pos2[0]], [pos2[1]], [pos2[2]], c='red', s=100, marker='o')
            self.ax_3d.set_xlabel('X (km)')
            self.ax_3d.set_ylabel('Y (km)')
            self.ax_3d.set_zlabel('Z (km)')
            self.ax_3d.set_title('3D Trajectory')
            
            # XY projection
            if len(traj1) > 1:
                self.ax_xy.plot(traj1[:, 0], traj1[:, 1], 'b-', alpha=0.5, linewidth=1, label='Star 1')
                self.ax_xy.plot(traj2[:, 0], traj2[:, 1], 'r-', alpha=0.5, linewidth=1, label='Star 2')
            
            self.ax_xy.scatter([pos1[0]], [pos1[1]], c='blue', s=100, marker='o')
            self.ax_xy.scatter([pos2[0]], [pos2[1]], c='red', s=100, marker='o')
            self.ax_xy.set_xlabel('X (km)')
            self.ax_xy.set_ylabel('Y (km)')
            self.ax_xy.set_title('XY Projection')
            self.ax_xy.grid(True)
            self.ax_xy.set_aspect('equal')
            self.ax_xy.legend()
        
        # Time series plots
        if len(self.simulator.separation_history) > 1:
            times = np.arange(len(self.simulator.separation_history)) * self.simulator.dt
            
            # Separation
            self.ax_sep.plot(times, self.simulator.separation_history, 'g-', linewidth=2)
            self.ax_sep.set_xlabel('Time (s)')
            self.ax_sep.set_ylabel('Separation (km)')
            self.ax_sep.set_title('Separation')
            self.ax_sep.grid(True)
            
            # Energy
            if len(self.simulator.energy_history) > 1:
                self.ax_energy.plot(times, self.simulator.energy_history, 'purple', linewidth=2)
                self.ax_energy.set_xlabel('Time (s)')
                self.ax_energy.set_ylabel('Total Energy (J)')
                self.ax_energy.set_title('Energy Conservation')
                self.ax_energy.grid(True)
            
            # Gravitational waves
            if len(self.simulator.gw_strain_history) > 1:
                self.ax_gw.plot(times, self.simulator.gw_strain_history, 'orange', linewidth=2)
                self.ax_gw.set_xlabel('Time (s)')
                self.ax_gw.set_ylabel('GW Strain (×10⁻²¹)')
                self.ax_gw.set_title('Gravitational Wave Signal')
                self.ax_gw.grid(True)
        
        plt.tight_layout()
        self.fig.canvas.draw_idle()


def main():
    """Main function to run the simulation"""
    print("Initializing Neutron Star Collision Simulation...")
    print("This simulation models binary neutron star mergers with adjustable parameters.")
    print("\nControls:")
    print("- Adjust sliders to change initial conditions")
    print("- Click 'Reset' to restart with new parameters")
    print("- Click 'Run' to start/stop the animation")
    print("\nNote: This is a simplified Newtonian simulation.")
    print("Full general relativistic effects require more complex codes.")
    
    simulator = NeutronStarSimulator()
    simulator.create_binary_system()
    
    visualizer = SimulationVisualizer(simulator)
    visualizer.update_plots()
    
    plt.show()


if __name__ == "__main__":
    main()

