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
PADDLE_SPEED = 8
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
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (60, 60, 60)
UI_BLUE = (70, 130, 180)
UI_PANEL = (245, 245, 250)
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
    
    def update(self, mouse_x):
        # Move paddle to follow mouse (centered on mouse position)
        target_x = mouse_x - self.width // 2
        
        # Keep paddle on screen
        self.x = max(0, min(WIDTH - self.width, target_x))
    
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

class HardTarget:
    def __init__(self, x, y, width, height, hits_required):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.hits_required = hits_required
        self.current_hits = 0
        self.broken = False
        # Track which balls have hit this target to prevent multiple hits per collision
        self.hit_balls = set()
        # Animation state
        self.animation_timer = 0
        self.animation_duration = 30  # Frames for break animation
        # Metallic colors - gradient from dark to lighter
        self.base_color = (80, 80, 100)  # Dark steel
        self.highlight_color = (150, 150, 180)  # Light steel
        self.damage_color = (200, 100, 100)  # Red tint when damaged
    
    def update_animation(self):
        """Update animation timer"""
        if self.broken and self.animation_timer < self.animation_duration:
            self.animation_timer += 1
    
    def draw(self, screen):
        if self.broken and self.animation_timer < self.animation_duration:
            # Draw break animation
            progress = self.animation_timer / self.animation_duration
            alpha = int(255 * (1 - progress))
            scale = 1.0 - progress * 0.5  # Shrink to 50%
            
            # Create particles effect
            particle_count = 8
            for i in range(particle_count):
                angle = (2 * math.pi * i) / particle_count
                distance = progress * 30
                px = int(self.x + self.width // 2 + math.cos(angle) * distance)
                py = int(self.y + self.height // 2 + math.sin(angle) * distance)
                particle_size = int(5 * (1 - progress))
                if particle_size > 0:
                    pygame.draw.circle(screen, self.highlight_color, (px, py), particle_size)
            
            # Draw fading/scaling brick
            scaled_width = int(self.width * scale)
            scaled_height = int(self.height * scale)
            scaled_x = int(self.x + (self.width - scaled_width) // 2)
            scaled_y = int(self.y + (self.height - scaled_height) // 2)
            
            # Create semi-transparent surface
            temp_surface = pygame.Surface((scaled_width, scaled_height))
            temp_surface.set_alpha(alpha)
            temp_surface.fill(self.base_color)
            screen.blit(temp_surface, (scaled_x, scaled_y))
            
        elif not self.broken:
            # Calculate damage percentage for visual feedback
            damage_ratio = self.current_hits / self.hits_required
            
            # Draw gradient background (metallic look)
            # Base color with damage tint
            base_r = int(self.base_color[0] + (self.damage_color[0] - self.base_color[0]) * damage_ratio * 0.3)
            base_g = int(self.base_color[1] + (self.damage_color[1] - self.base_color[1]) * damage_ratio * 0.3)
            base_b = int(self.base_color[2] + (self.damage_color[2] - self.base_color[2]) * damage_ratio * 0.3)
            base_color = (base_r, base_g, base_b)
            
            # Main body with gradient effect
            pygame.draw.rect(screen, base_color, (self.x, self.y, self.width, self.height))
            
            # Top highlight (metallic shine)
            highlight_rect = pygame.Rect(self.x, self.y, self.width, self.height // 3)
            highlight_surface = pygame.Surface((self.width, self.height // 3))
            highlight_surface.set_alpha(100)
            highlight_surface.fill(self.highlight_color)
            screen.blit(highlight_surface, (self.x, self.y))
            
            # Border with gradient
            border_width = 4
            pygame.draw.rect(screen, self.highlight_color, (self.x, self.y, self.width, border_width))  # Top
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 3)  # Outer border
            
            # Inner border for depth
            inner_border = 2
            pygame.draw.rect(screen, (60, 60, 80), (self.x + inner_border, self.y + inner_border, 
                                                     self.width - inner_border * 2, self.height - inner_border * 2), 1)
            
            # Draw hits remaining with glow effect
            font = pygame.font.Font(None, 28)
            hits_text = f"{self.hits_required - self.current_hits}"
            
            # Text shadow
            shadow_surface = font.render(hits_text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(center=(self.x + self.width // 2 + 2, self.y + self.height // 2 + 2))
            screen.blit(shadow_surface, shadow_rect)
            
            # Main text
            text_color = WHITE if damage_ratio < 0.5 else (255, 200, 200)  # Red tint when damaged
            text_surface = font.render(hits_text, True, text_color)
            text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(text_surface, text_rect)
            
            # Draw life icon indicator with better styling
            small_font = pygame.font.Font(None, 18)
            life_text = small_font.render("+1 LIFE", True, GREEN)
            # Add shadow
            shadow = small_font.render("+1 LIFE", True, (0, 50, 0))
            shadow_rect = shadow.get_rect(center=(self.x + self.width // 2 + 1, self.y + self.height - 10 + 1))
            screen.blit(shadow, shadow_rect)
            life_rect = life_text.get_rect(center=(self.x + self.width // 2, self.y + self.height - 10))
            screen.blit(life_text, life_rect)
    
    def check_collision(self, ball):
        if not self.broken:
            # Check if ball collides with hard target
            is_colliding = (ball.y - ball.radius <= self.y + self.height and 
                          ball.y + ball.radius >= self.y and
                          ball.x + ball.radius >= self.x and 
                          ball.x - ball.radius <= self.x + self.width)
            
            if is_colliding:
                # Only count hit if ball is moving toward target and hasn't been counted yet
                # This prevents multiple hits while ball is stuck in collision area
                if ball.vy > 0.5 and id(ball) not in self.hit_balls:  # Ball moving down with some speed
                    self.current_hits += 1
                    self.hit_balls.add(id(ball))
                    
                    # Check if broken
                    if self.current_hits >= self.hits_required:
                        self.broken = True
                        return True  # Signal that a life should be added
                
                # Bounce ball away properly (only if ball is moving toward target)
                if ball.vy > 0:  # Ball is moving down toward target
                    # Full bounce with proper physics
                    ball.vy = -abs(ball.vy) * 1.0  # Full bounce, no damping
                    # Also push ball away from center of target slightly
                    if ball.x < self.x + self.width // 2:
                        ball.vx -= 1.5  # Push left
                    else:
                        ball.vx += 1.5  # Push right
                    # Ensure ball is above target to prevent getting stuck
                    if ball.y < self.y + self.height:
                        ball.y = self.y - ball.radius
            else:
                # Ball is no longer colliding, remove from set so it can hit again if it comes back
                self.hit_balls.discard(id(ball))
        return False

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
    instructions_panel_height = 80
    paddle_y = HEIGHT - instructions_panel_height - 30  # Position paddle above instructions panel
    paddle = Paddle(WIDTH // 2 - paddle_width // 2, paddle_y, paddle_width, paddle_height)
    
    # Create targets
    targets = []
    num_targets = 6
    target_spacing = WIDTH // (num_targets + 1)
    target_y = 80  # Moved down to avoid UI overlap
    for i in range(num_targets):
        x = target_spacing * (i + 1) - TARGET_WIDTH // 2
        y = target_y
        points = (num_targets - i) * 10  # More points for targets on the right
        targets.append(Target(x, y, TARGET_WIDTH, TARGET_HEIGHT, points))
    
    # Create hard target (special brick that gives lives)
    hard_target_hits_required = 8  # Starts at 8 hits (much harder), increases each time
    hard_target_x = WIDTH // 2 - TARGET_WIDTH // 2  # Center position
    hard_target = HardTarget(hard_target_x, target_y + TARGET_HEIGHT + 10, TARGET_WIDTH, TARGET_HEIGHT, hard_target_hits_required)
    
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
    
    # Ball spawn settings
    ball_spawn_timer = 0
    ball_spawn_interval = 180  # Spawn new ball every 3 seconds (180 frames at 60 FPS)
    balls_per_spawn = 1  # Number of balls to spawn at once (user controllable)
    
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
                        y = target_y
                        points = (num_targets - i) * 10
                        targets.append(Target(x, y, TARGET_WIDTH, TARGET_HEIGHT, points))
                    # Reset hard target
                    hard_target_hits_required = 8
                    hard_target = HardTarget(hard_target_x, target_y + TARGET_HEIGHT + 10, TARGET_WIDTH, TARGET_HEIGHT, hard_target_hits_required)
                    ball_spawn_timer = 0
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    # Increase balls per spawn (max 5)
                    balls_per_spawn = min(5, balls_per_spawn + 1)
                elif event.key == pygame.K_MINUS:
                    # Decrease balls per spawn (min 1)
                    balls_per_spawn = max(1, balls_per_spawn - 1)
                elif event.key == pygame.K_LEFTBRACKET:
                    # Alternative: decrease with [
                    balls_per_spawn = max(1, balls_per_spawn - 1)
                elif event.key == pygame.K_RIGHTBRACKET:
                    # Alternative: increase with ]
                    balls_per_spawn = min(5, balls_per_spawn + 1)
        
        if not game_over and not paused:
            # Get mouse position for paddle control
            mouse_x, _ = pygame.mouse.get_pos()
            paddle.update(mouse_x)
            
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
                
                # Check if ball hit hard target
                hard_target.check_collision(ball)
            
            # Update hard target animation
            hard_target.update_animation()
            
            # Check if hard target was just broken (give life, but don't respawn yet)
            if hard_target.broken and hard_target.animation_timer == 1:
                # Hard target was broken, add a life
                lives += 1
                # Increase difficulty for next time (but don't respawn until round ends)
                hard_target_hits_required += 1
            
            # Check collisions between balls
            for i in range(len(balls)):
                for j in range(i + 1, len(balls)):
                    balls[i].collide(balls[j])
            
            # Remove balls that fall below paddle (lost)
            for ball in balls:
                if ball.y > paddle.y + paddle.height + 30:  # Ball is definitely lost
                    if ball not in balls_to_remove:  # Only count once per ball
                        balls_to_remove.append(ball)
            
            # Remove fallen balls
            for ball in balls_to_remove:
                balls.remove(ball)
            
            # Only lose a life if ALL balls are gone
            if len(balls) == 0 and len(balls_to_remove) > 0:
                lives -= 1
                if lives <= 0:
                    game_over = True
            
            # Spawn new balls periodically
            ball_spawn_timer += 1
            if ball_spawn_timer >= ball_spawn_interval:
                # Spawn the configured number of balls (respecting max limit)
                balls_to_spawn = min(balls_per_spawn, 8 - len(balls))
                for _ in range(balls_to_spawn):
                    if len(balls) < 8:
                        spawn_ball()
                ball_spawn_timer = 0
            
            # Check if all targets are hit (win condition)
            if all(target.hit for target in targets):
                # Reset targets with more points
                targets = []
                for i in range(num_targets):
                    x = target_spacing * (i + 1) - TARGET_WIDTH // 2
                    y = target_y
                    points = (num_targets - i) * 10 + score // 100  # Increase points over time
                    targets.append(Target(x, y, TARGET_WIDTH, TARGET_HEIGHT, points))
                # Respawn hard target when targets reset (new round) - always respawn for new formation
                hard_target = HardTarget(hard_target_x, target_y + TARGET_HEIGHT + 10, TARGET_WIDTH, TARGET_HEIGHT, hard_target_hits_required)
        
        # Draw everything
        screen.fill(WHITE)
        
        # Draw top UI bar
        ui_bar_height = 60
        pygame.draw.rect(screen, UI_PANEL, (0, 0, WIDTH, ui_bar_height))
        pygame.draw.line(screen, DARK_GRAY, (0, ui_bar_height), (WIDTH, ui_bar_height), 2)
        
        # Draw score and lives in UI bar
        title_font = pygame.font.Font(None, 32)
        label_font = pygame.font.Font(None, 24)
        value_font = pygame.font.Font(None, 36)
        
        # Score panel
        score_label = label_font.render("SCORE", True, DARK_GRAY)
        score_value = value_font.render(str(score), True, UI_BLUE)
        screen.blit(score_label, (20, 8))
        screen.blit(score_value, (20, 30))
        
        # Lives panel
        lives_label = label_font.render("LIVES", True, DARK_GRAY)
        lives_color = RED if lives <= 1 else GREEN if lives == 3 else ORANGE
        lives_value = value_font.render(str(lives), True, lives_color)
        screen.blit(lives_label, (180, 8))
        screen.blit(lives_value, (180, 30))
        
        # Spawn count panel
        spawn_label = label_font.render("SPAWN", True, DARK_GRAY)
        spawn_value = value_font.render(f"{balls_per_spawn}x", True, PURPLE)
        screen.blit(spawn_label, (340, 8))
        screen.blit(spawn_value, (340, 30))
        
        # Draw targets
        for target in targets:
            target.draw(screen)
        
        # Draw hard target
        hard_target.draw(screen)
        
        # Draw balls
        for ball in balls:
            ball.draw(screen)
        
        # Draw instructions at bottom (only when not game over) - draw before paddle
        if not game_over:
            # Instructions panel at bottom
            instructions_y = HEIGHT - instructions_panel_height
            pygame.draw.rect(screen, UI_PANEL, (0, instructions_y, WIDTH, instructions_panel_height))
            pygame.draw.line(screen, DARK_GRAY, (0, instructions_y), (WIDTH, instructions_y), 2)
            
            small_font = pygame.font.Font(None, 20)
            instructions = [
                "Mouse: Move Paddle",
                "SPACE: Pause",
                "R: Restart",
                "ESC: Quit",
                "+/- or [/]: Spawn Count",
                f"Current: {balls_per_spawn}x"
            ]
            # Center instructions in 3 columns
            start_x = WIDTH // 2 - 150
            for i, text in enumerate(instructions):
                col = i % 3
                row = i // 3
                text_surface = small_font.render(text, True, DARK_GRAY)
                screen.blit(text_surface, (start_x + col * 200, instructions_y + 15 + row * 25))
        
        # Draw paddle (after instructions so it appears on top)
        if not game_over:
            paddle.draw(screen)
        
        # Draw game over or paused overlay
        if game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            game_over_font = pygame.font.Font(None, 72)
            game_over_text = game_over_font.render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(game_over_text, text_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            screen.blit(restart_text, restart_rect)
        elif paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            
            pause_font = pygame.font.Font(None, 64)
            pause_text = pause_font.render("PAUSED", True, UI_BLUE)
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()

