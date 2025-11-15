import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
BOUNCE_DAMPING = 0.9  # Energy loss on bounce
FRICTION = 0.99  # Ground friction

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]

class Ball:
    def __init__(self, x, y, radius=None, color=None):
        self.x = x
        self.y = y
        self.radius = radius if radius else random.randint(15, 30)
        self.color = color if color else random.choice(COLORS)
        
        # Velocity
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -5)
        
        # Mass (proportional to area)
        self.mass = math.pi * self.radius ** 2
    
    def update(self):
        # Apply gravity
        self.vy += GRAVITY
        
        # Apply friction if on ground
        if self.y + self.radius >= HEIGHT - 10:
            self.vx *= FRICTION
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.vx = -self.vx * BOUNCE_DAMPING
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        
        # Bounce off ground and ceiling
        if self.y - self.radius <= 0:
            self.vy = -self.vy * BOUNCE_DAMPING
            self.y = self.radius
        elif self.y + self.radius >= HEIGHT - 10:
            self.vy = -self.vy * BOUNCE_DAMPING
            self.y = HEIGHT - 10 - self.radius
            
            # Stop tiny bounces
            if abs(self.vy) < 0.5:
                self.vy = 0
            if abs(self.vx) < 0.1:
                self.vx = 0
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
    
    def collide(self, other):
        # Calculate distance between centers
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if colliding
        if distance < self.radius + other.radius:
            # Calculate collision angle
            if distance == 0:
                angle = random.uniform(0, 2 * math.pi)
            else:
                angle = math.atan2(dy, dx)
            
            # Separate balls to prevent overlap
            overlap = (self.radius + other.radius) - distance
            self.x -= overlap * math.cos(angle) * 0.5
            self.y -= overlap * math.sin(angle) * 0.5
            other.x += overlap * math.cos(angle) * 0.5
            other.y += overlap * math.sin(angle) * 0.5
            
            # Calculate velocities in collision frame
            # Relative velocity
            dvx = other.vx - self.vx
            dvy = other.vy - self.vy
            
            # Relative velocity in collision normal direction
            dot_product = dvx * math.cos(angle) + dvy * math.sin(angle)
            
            # Don't resolve if velocities are separating
            if dot_product > 0:
                return
            
            # Collision impulse
            impulse = (2 * dot_product) / (self.mass + other.mass)
            
            # Update velocities (elastic collision)
            self.vx += impulse * other.mass * math.cos(angle) * BOUNCE_DAMPING
            self.vy += impulse * other.mass * math.sin(angle) * BOUNCE_DAMPING
            other.vx -= impulse * self.mass * math.cos(angle) * BOUNCE_DAMPING
            other.vy -= impulse * self.mass * math.sin(angle) * BOUNCE_DAMPING

def main():
    # Set up the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bouncing Balls Simulation")
    clock = pygame.time.Clock()
    
    # Create balls
    balls = []
    num_balls = 10
    
    for _ in range(num_balls):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, HEIGHT // 2)
        balls.append(Ball(x, y))
    
    # Main game loop
    running = True
    paused = False
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset simulation
                    balls = []
                    for _ in range(num_balls):
                        x = random.randint(50, WIDTH - 50)
                        y = random.randint(50, HEIGHT // 2)
                        balls.append(Ball(x, y))
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Add a new ball at mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                balls.append(Ball(mouse_x, mouse_y))
        
        if not paused:
            # Update balls
            for ball in balls:
                ball.update()
            
            # Check collisions between balls
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    balls[i].collide(balls[j])
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw ground line
        pygame.draw.line(screen, BLACK, (0, HEIGHT - 10), (WIDTH, HEIGHT - 10), 2)
        
        # Draw balls
        for ball in balls:
            ball.draw(screen)
        
        # Draw instructions
        font = pygame.font.Font(None, 24)
        instructions = [
            "SPACE: Pause/Resume",
            "R: Reset",
            "Click: Add Ball",
            "ESC: Quit"
        ]
        for i, text in enumerate(instructions):
            text_surface = font.render(text, True, BLACK)
            screen.blit(text_surface, (10, 10 + i * 25))
        
        if paused:
            pause_text = font.render("PAUSED", True, RED)
            screen.blit(pause_text, (WIDTH // 2 - 50, 20))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()

