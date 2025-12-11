"""
Example usage of the neutron star collision simulation
This shows how to use the simulator programmatically (without GUI)
"""

from neutron_star_simulation import NeutronStarSimulator
import matplotlib.pyplot as plt
import numpy as np

def run_example_simulation():
    """Run a simple example simulation"""
    print("Running example neutron star collision simulation...")
    
    # Create simulator
    simulator = NeutronStarSimulator()
    
    # Create a binary system with specific parameters
    simulator.create_binary_system(
        mass1=1.4,          # Solar masses
        mass2=1.4,          # Solar masses
        separation=50.0,   # km (close initial separation)
        eccentricity=0.0,   # Circular orbit
        inclination=0.0,   # Face-on view
        phase=0.0          # Initial phase
    )
    
    # Run simulation
    print("Running simulation...")
    num_steps = 50000
    simulator.run_simulation(num_steps)
    
    # Plot results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Trajectory (XY projection)
    if len(simulator.trajectory_history[0]) > 0:
        traj1 = np.array(simulator.trajectory_history[0])
        traj2 = np.array(simulator.trajectory_history[1])
        
        axes[0, 0].plot(traj1[:, 0], traj1[:, 1], 'b-', label='Star 1', linewidth=1.5)
        axes[0, 0].plot(traj2[:, 0], traj2[:, 1], 'r-', label='Star 2', linewidth=1.5)
        axes[0, 0].scatter([traj1[0, 0]], [traj1[0, 1]], c='blue', s=100, marker='o', zorder=5)
        axes[0, 0].scatter([traj2[0, 0]], [traj2[0, 1]], c='red', s=100, marker='o', zorder=5)
        axes[0, 0].scatter([traj1[-1, 0]], [traj1[-1, 1]], c='blue', s=100, marker='*', zorder=5)
        axes[0, 0].scatter([traj2[-1, 0]], [traj2[-1, 1]], c='red', s=100, marker='*', zorder=5)
        axes[0, 0].set_xlabel('X (km)')
        axes[0, 0].set_ylabel('Y (km)')
        axes[0, 0].set_title('Orbital Trajectory (XY Projection)')
        axes[0, 0].grid(True)
        axes[0, 0].legend()
        axes[0, 0].set_aspect('equal')
    
    # Separation vs time
    if len(simulator.separation_history) > 0:
        times = np.arange(len(simulator.separation_history)) * simulator.dt
        axes[0, 1].plot(times, simulator.separation_history, 'g-', linewidth=2)
        axes[0, 1].axhline(y=simulator.stars[0].radius + simulator.stars[1].radius, 
                          color='r', linestyle='--', label='Contact')
        axes[0, 1].set_xlabel('Time (s)')
        axes[0, 1].set_ylabel('Separation (km)')
        axes[0, 1].set_title('Orbital Decay')
        axes[0, 1].grid(True)
        axes[0, 1].legend()
    
    # Energy vs time
    if len(simulator.energy_history) > 0:
        times = np.arange(len(simulator.energy_history)) * simulator.dt
        axes[1, 0].plot(times, np.array(simulator.energy_history) / 1e44, 'purple', linewidth=2)
        axes[1, 0].set_xlabel('Time (s)')
        axes[1, 0].set_ylabel('Total Energy (×10⁴⁴ J)')
        axes[1, 0].set_title('Energy Evolution')
        axes[1, 0].grid(True)
    
    # Gravitational wave strain
    if len(simulator.gw_strain_history) > 0:
        times = np.arange(len(simulator.gw_strain_history)) * simulator.dt
        axes[1, 1].plot(times, simulator.gw_strain_history, 'orange', linewidth=2)
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('GW Strain (×10⁻²¹)')
        axes[1, 1].set_title('Gravitational Wave Signal')
        axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig('example_simulation_results.png', dpi=150)
    print("Results saved to 'example_simulation_results.png'")
    print(f"Final separation: {simulator.separation_history[-1]:.2f} km")
    print(f"Initial separation: {simulator.separation_history[0]:.2f} km")
    print(f"Total simulation time: {simulator.time:.2f} seconds")
    
    plt.show()

if __name__ == "__main__":
    run_example_simulation()

