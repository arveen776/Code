"""
Physics engine for gravity simulation.
Handles gravitational force calculations and particle dynamics.
"""

import math

G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
# For visualization, we'll use a scaled version
G_SCALED = 100.0  # Scaled gravitational constant for better visualization


class Body:
    """Represents a gravitational body with mass."""
    
    def __init__(self, x, y, mass, radius=10):
        """
        Initialize a gravitational body.
        
        Args:
            x: X position
            y: Y position
            mass: Mass of the body
            radius: Visual radius of the body
        """
        self.x = x
        self.y = y
        self.mass = mass
        self.radius = radius
    
    def get_position(self):
        """Get the position of the body."""
        return (self.x, self.y)


class Particle:
    """Represents a particle that experiences gravitational forces."""
    
    def __init__(self, x, y, vx=0, vy=0, mass=1.0, radius=3):
        """
        Initialize a particle.
        
        Args:
            x: Initial X position
            y: Initial Y position
            vx: Initial X velocity
            vy: Initial Y velocity
            mass: Mass of the particle (usually negligible)
            radius: Visual radius
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.radius = radius
        self.trajectory = [(x, y)]  # Store trajectory points
    
    def update(self, bodies, dt):
        """
        Update particle position based on gravitational forces.
        
        Args:
            bodies: List of Body objects that exert gravitational force
            dt: Time step
        """
        fx = 0
        fy = 0
        
        # Calculate total gravitational force from all bodies
        for body in bodies:
            dx = body.x - self.x
            dy = body.y - self.y
            r_squared = dx * dx + dy * dy
            
            # Avoid division by zero
            if r_squared < 1:
                r_squared = 1
            
            r = math.sqrt(r_squared)
            
            # Calculate gravitational force magnitude
            # F = G * m1 * m2 / r^2
            force_magnitude = G_SCALED * body.mass * self.mass / r_squared
            
            # Calculate force components
            fx += force_magnitude * (dx / r)
            fy += force_magnitude * (dy / r)
        
        # Update velocity (F = ma, so a = F/m)
        self.vx += fx / self.mass * dt
        self.vy += fy / self.mass * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Store trajectory point
        self.trajectory.append((self.x, self.y))
        
        # Limit trajectory length to prevent memory issues
        if len(self.trajectory) > 1000:
            self.trajectory = self.trajectory[-1000:]


class PhysicsEngine:
    """Main physics engine for the simulation."""
    
    def __init__(self):
        """Initialize the physics engine."""
        self.bodies = []
        self.particles = []
        self.dt = 0.1  # Time step
    
    def add_body(self, body):
        """Add a gravitational body to the simulation."""
        self.bodies.append(body)
    
    def add_particle(self, particle):
        """Add a particle to the simulation."""
        self.particles.append(particle)
    
    def clear_particles(self):
        """Clear all particles."""
        self.particles = []
    
    def update(self):
        """Update the simulation by one time step."""
        for particle in self.particles:
            particle.update(self.bodies, self.dt)
    
    def get_bodies(self):
        """Get all bodies."""
        return self.bodies
    
    def get_particles(self):
        """Get all particles."""
        return self.particles

