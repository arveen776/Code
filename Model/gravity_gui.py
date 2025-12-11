"""
GUI application for gravity simulation.
Allows visualization of gravitational interactions between bodies and particles.
"""

import tkinter as tk
from tkinter import ttk
from physics_engine import PhysicsEngine, Body, Particle


class GravityGUI:
    """Main GUI application for gravity simulation."""
    
    def __init__(self, root):
        """
        Initialize the GUI.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Gravity Simulation")
        self.root.geometry("1200x800")
        
        # Physics engine
        self.engine = PhysicsEngine()
        
        # Canvas dimensions
        self.canvas_width = 800
        self.canvas_height = 600
        
        # Simulation state (must be before setup_ui)
        self.is_running = True  # Start running by default
        self.simulation_speed = 1.0
        
        # Setup UI
        self.setup_ui()
        
        # Mouse state for particle placement
        self.placing_particle = False
        
        # Start simulation loop
        self.simulate()
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Control panel (left side)
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Parameters section (kept for future extensibility)
        # Individual mass controls are now in Body and Particle sections
        
        # Body controls
        body_frame = ttk.LabelFrame(control_frame, text="Body", padding="10")
        body_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Body mass input
        body_mass_frame = ttk.Frame(body_frame)
        body_mass_frame.pack(fill=tk.X, pady=5)
        ttk.Label(body_mass_frame, text="Body Mass:").pack(side=tk.LEFT)
        self.body_mass_var = tk.DoubleVar(value=1000.0)  # Default body mass
        body_mass_entry = ttk.Entry(body_mass_frame, textvariable=self.body_mass_var, width=10)
        body_mass_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(body_mass_frame, text="kg").pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(body_frame, text="Place Body at Center", 
                  command=self.place_body_center).pack(fill=tk.X, pady=2)
        ttk.Button(body_frame, text="Clear Bodies", 
                  command=self.clear_bodies).pack(fill=tk.X, pady=2)
        
        # Particle controls
        particle_frame = ttk.LabelFrame(control_frame, text="Particles", padding="10")
        particle_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Particle mass input
        particle_mass_frame = ttk.Frame(particle_frame)
        particle_mass_frame.pack(fill=tk.X, pady=5)
        ttk.Label(particle_mass_frame, text="Particle Mass:").pack(side=tk.LEFT)
        self.particle_mass_var = tk.DoubleVar(value=1.0)
        particle_mass_entry = ttk.Entry(particle_mass_frame, textvariable=self.particle_mass_var, width=10)
        particle_mass_entry.pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(particle_mass_frame, text="kg").pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Button(particle_frame, text="Place Particle (Click Canvas)", 
                  command=self.toggle_particle_placement).pack(fill=tk.X, pady=2)
        ttk.Button(particle_frame, text="Clear Particles", 
                  command=self.clear_particles).pack(fill=tk.X, pady=2)
        ttk.Button(particle_frame, text="Clear Trajectories", 
                  command=self.clear_trajectories).pack(fill=tk.X, pady=2)
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(control_frame, text="Simulation", padding="10")
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.play_pause_btn = ttk.Button(sim_frame, text="Pause", 
                                         command=self.toggle_simulation)
        self.play_pause_btn.pack(fill=tk.X, pady=2)
        
        ttk.Button(sim_frame, text="Reset", command=self.reset_simulation).pack(fill=tk.X, pady=2)
        
        # Speed control
        speed_frame = ttk.Frame(sim_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        ttk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=self.simulation_speed)
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, 
                               variable=self.speed_var, orient=tk.HORIZONTAL,
                               command=self.on_speed_change)
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.speed_label = ttk.Label(speed_frame, text=f"{self.simulation_speed:.1f}x")
        self.speed_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Canvas (right side)
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, 
                               height=self.canvas_height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Instructions
        info_label = ttk.Label(control_frame, 
                              text="Instructions:\n\n"
                                   "1. Set body mass and place body\n"
                                   "2. Set particle mass\n"
                                   "3. Click 'Place Particle' then\n"
                                   "   click on canvas to add particles\n"
                                   "4. Watch the simulation!\n\n"
                                   "Simulation runs automatically.",
                              justify=tk.LEFT)
        info_label.pack(fill=tk.X, pady=(10, 0))
    
    
    def on_speed_change(self, value=None):
        """Handle simulation speed change."""
        self.simulation_speed = self.speed_var.get()
        self.speed_label.config(text=f"{self.simulation_speed:.1f}x")
    
    def place_body_center(self):
        """Place a body at the center of the canvas."""
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        body_mass = self.body_mass_var.get()
        if body_mass <= 0:
            body_mass = 1000.0  # Default if invalid
            self.body_mass_var.set(body_mass)
        body = Body(center_x, center_y, body_mass)
        self.engine.add_body(body)
    
    def clear_bodies(self):
        """Clear all bodies."""
        self.engine.bodies = []
    
    def toggle_particle_placement(self):
        """Toggle particle placement mode."""
        self.placing_particle = not self.placing_particle
        if self.placing_particle:
            self.canvas.config(cursor="crosshair")
        else:
            self.canvas.config(cursor="")
    
    def clear_particles(self):
        """Clear all particles."""
        self.engine.clear_particles()
    
    def clear_trajectories(self):
        """Clear particle trajectories."""
        for particle in self.engine.get_particles():
            particle.trajectory = [(particle.x, particle.y)]
    
    def toggle_simulation(self):
        """Toggle simulation play/pause."""
        self.is_running = not self.is_running
        self.play_pause_btn.config(text="Play" if not self.is_running else "Pause")
    
    def reset_simulation(self):
        """Reset the simulation."""
        self.clear_particles()
        self.clear_bodies()
        self.is_running = False
        self.play_pause_btn.config(text="Pause")
    
    def on_canvas_click(self, event):
        """Handle canvas click events."""
        if self.placing_particle:
            # Place particle at click location with specified mass
            particle_mass = self.particle_mass_var.get()
            if particle_mass <= 0:
                particle_mass = 1.0  # Default if invalid
                self.particle_mass_var.set(particle_mass)
            particle = Particle(event.x, event.y, vx=0, vy=0, mass=particle_mass)
            self.engine.add_particle(particle)
            self.placing_particle = False
            self.canvas.config(cursor="")
    
    def on_canvas_motion(self, event):
        """Handle canvas mouse motion."""
        pass
    
    def draw(self):
        """Draw all objects on the canvas."""
        self.canvas.delete("all")
        
        # Draw bodies
        for body in self.engine.get_bodies():
            x, y = body.x, body.y
            # Draw body as a circle (size proportional to mass)
            radius = max(10, min(30, body.mass / 100))  # Scale radius with mass
            self.canvas.create_oval(x - radius, y - radius,
                                   x + radius, y + radius,
                                   fill="yellow", outline="orange", width=2)
            # Draw mass label
            self.canvas.create_text(x, y - radius - 15,
                                   text=f"M={body.mass:.1f}kg",
                                   fill="white", font=("Arial", 8))
        
        # Draw particles and trajectories
        for particle in self.engine.get_particles():
            # Draw trajectory
            if len(particle.trajectory) > 1:
                trajectory_points = []
                for tx, ty in particle.trajectory[-500:]:  # Last 500 points
                    trajectory_points.extend([tx, ty])
                if len(trajectory_points) > 2:
                    self.canvas.create_line(*trajectory_points, fill="cyan", width=1, smooth=True)
            
            # Draw particle (size proportional to mass)
            x, y = particle.x, particle.y
            radius = max(2, min(8, particle.mass / 2))
            self.canvas.create_oval(x - radius, y - radius,
                                   x + radius, y + radius,
                                   fill="white", outline="cyan", width=1)
            # Draw mass label for particles
            if particle.mass > 1.0:
                self.canvas.create_text(x, y - radius - 10,
                                       text=f"m={particle.mass:.1f}kg",
                                       fill="white", font=("Arial", 7))
    
    def simulate(self):
        """Main simulation loop."""
        if self.is_running:
            # Update simulation multiple times based on speed
            for _ in range(int(self.simulation_speed)):
                self.engine.update()
        
        # Draw everything
        self.draw()
        
        # Schedule next update
        self.root.after(16, self.simulate)  # ~60 FPS


def main():
    """Main entry point."""
    root = tk.Tk()
    app = GravityGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

