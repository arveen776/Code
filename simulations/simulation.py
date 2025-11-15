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
PADDLE_SPEED = 15
TARGET_WIDTH = 80
TARGET_HEIGHT = 30

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
GRAY = (128, 128, 128)
DARK_GREEN = (0, 200, 0)
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
    
    def update(self, allow_bottom_bounce=True):
        # Apply gravity
        self.vy += GRAVITY
        
        # Apply friction if on ground
        if allow_bottom_bounce and self.y + self.radius >= HEIGHT - 10:
            self.vx *= FRICTION
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off walls
        if self.x - self.radius <= 0 or self.x + self.radius >= WIDTH:
            self.vx = -self.vx * BOUNCE_DAMPING
            self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        
        # Bounce off ceiling
        if self.y - self.radius <= 0:
            self.vy = -self.vy * BOUNCE_DAMPING
            self.y = self.radius
        
        # Bounce off ground (only if allowed)
        if allow_bottom_bounce and self.y + self.radius >= HEIGHT - 10:
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

class Paddle:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = PADDLE_SPEED
    
    def update(self, keys):
        # Move paddle left/right
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        
        # Keep paddle on screen
        self.x = max(0, min(WIDTH - self.width, self.x))
    
    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)
    
    def check_collision(self, ball):
        # Check if ball collides with paddle
        if (ball.y + ball.radius >= self.y and 
            ball.y - ball.radius <= self.y + self.height and
            ball.x + ball.radius >= self.x and 
            ball.x - ball.radius <= self.x + self.width):
            
            # Bounce ball up
            ball.vy = -abs(ball.vy) * 1.2  # Give it extra boost
            ball.y = self.y - ball.radius
            
            # Add horizontal velocity based on where ball hits paddle
            hit_pos = (ball.x - self.x) / self.width  # 0 to 1
            ball.vx += (hit_pos - 0.5) * 5  # Add velocity based on hit position
            
            return True
        return False

class Target:
    def __init__(self, x, y, width, height, points):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.points = points
        self.hit = False
        self.color = random.choice([RED, GREEN, YELLOW, PURPLE, CYAN])
    
    def draw(self, screen):
        if not self.hit:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
            
            # Draw points text
            font = pygame.font.Font(None, 20)
            text = font.render(str(self.points), True, BLACK)
            text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text, text_rect)
    
    def check_collision(self, ball):
        if not self.hit:
            # Check if ball collides with target
            if (ball.y - ball.radius <= self.y + self.height and 
                ball.y + ball.radius >= self.y and
                ball.x + ball.radius >= self.x and 
                ball.x - ball.radius <= self.x + self.width):
                
                self.hit = True
                # Bounce ball away
                ball.vy = -abs(ball.vy) * 0.8
                return self.points
        return 0

def main():
    # Set up the screen
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Bounce Game")
    clock = pygame.time.Clock()
    
    # Game state
    score = 0
    lives = 3
    game_over = False
    paused = False
    
    # Create paddle
    paddle_width = 120
    paddle_height = 20
    paddle = Paddle(WIDTH // 2 - paddle_width // 2, HEIGHT - 40, paddle_width, paddle_height)
    
    # Create targets
    targets = []
    num_targets = 6
    target_spacing = WIDTH // (num_targets + 1)
    for i in range(num_targets):
        x = target_spacing * (i + 1) - TARGET_WIDTH // 2
        y = 30
        points = (num_targets - i) * 10  # More points for targets on the right
        targets.append(Target(x, y, TARGET_WIDTH, TARGET_HEIGHT, points))
    
    # Create balls
    balls = []
    num_balls = 3
    
    def spawn_ball():
        x = random.randint(50, WIDTH - 50)
        y = random.randint(100, 200)
        balls.append(Ball(x, y))
    
    # Initial balls
    for _ in range(num_balls):
        spawn_ball()
    
    # Ball spawn timer
    ball_spawn_timer = 0
    ball_spawn_interval = 180  # Spawn new ball every 3 seconds (180 frames at 60 FPS)
    
    # Main game loop
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not game_over:
                    paused = not paused
                elif event.key == pygame.K_r:
                    # Reset game
                    score = 0
                    lives = 3
                    game_over = False
                    paused = False
                    balls = []
                    for _ in range(num_balls):
                        spawn_ball()
                    targets = []
                    for i in range(num_targets):
                        x = target_spacing * (i + 1) - TARGET_WIDTH // 2
                        y = 30
                        points = (num_targets - i) * 10
                        targets.append(Target(x, y, TARGET_WIDTH, TARGET_HEIGHT, points))
                    ball_spawn_timer = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False
        
        if not game_over and not paused:
            # Get keyboard state for continuous movement
            keys = pygame.key.get_pressed()
            paddle.update(keys)
            
            # Update balls
            balls_to_remove = []
            for ball in balls:
                ball.update(allow_bottom_bounce=False)  # Don't bounce off bottom in game mode
                
                # Check if ball hit paddle
                if paddle.check_collision(ball):
                    pass  # Paddle collision handled in method
                
                # Check if ball hit targets
                for target in targets:
                    points = target.check_collision(ball)
                    if points > 0:
                        score += points
            
            # Check collisions between balls
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    balls[i].collide(balls[j])
            
            # Remove balls that fall below paddle (lost)
            for ball in balls:
                if ball.y > paddle.y + paddle.height + 30:  # Ball is definitely lost
                    if ball not in balls_to_remove:  # Only count once per ball
                        balls_to_remove.append(ball)
                        lives -= 1
                        if lives <= 0:
                            game_over = True
                            break  # Stop checking once game over
            
            # Remove fallen balls
            for ball in balls_to_remove:
                balls.remove(ball)
            
            # Spawn new balls periodically
            ball_spawn_timer += 1
            if ball_spawn_timer >= ball_spawn_interval and len(balls) < 8:
                spawn_ball()
                ball_spawn_timer = 0
            
            # Check if all targets are hit (win condition)
            if all(target.hit for target in targets):
                # Reset targets with more points
                targets = []
                for i in range(num_targets):
                    x = target_spacing * (i + 1) - TARGET_WIDTH // 2
                    y = 30
                    points = (num_targets - i) * 10 + score // 100  # Increase points over time
                    targets.append(Target(x, y, TARGET_WIDTH, TARGET_HEIGHT, points))
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw targets
        for target in targets:
            target.draw(screen)
        
        # Draw paddle
        if not game_over:
            paddle.draw(screen)
        
        # Draw balls
        for ball in balls:
            ball.draw(screen)
        
        # Draw UI
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        lives_text = font.render(f"Lives: {lives}", True, RED if lives <= 1 else BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 50))
        
        # Draw game over or paused
        if game_over:
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(game_over_text, text_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart", True, BLACK)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            screen.blit(restart_text, restart_rect)
        elif paused:
            pause_font = pygame.font.Font(None, 48)
            pause_text = pause_font.render("PAUSED", True, BLUE)
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, pause_rect)
        
        # Draw instructions
        if not game_over:
            small_font = pygame.font.Font(None, 24)
            instructions = [
                "Arrow Keys / A/D: Move Paddle",
                "SPACE: Pause",
                "R: Restart",
                "ESC: Quit"
            ]
            for i, text in enumerate(instructions):
                text_surface = small_font.render(text, True, GRAY)
                screen.blit(text_surface, (WIDTH - 250, 10 + i * 25))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()

