
import pygame
import math
import random
import sys
from enum import Enum
# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Game Constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60
GRAVITY = 0.5
BOUNCE_DAMPING = 0.85
PADDLE_SPEED = 20
BALL_RADIUS = 12

# Colors (Neon Theme)
class Colors:
    BLACK = (0, 0, 0)
    DARK_BG = (10, 10, 20)
    WHITE = (255, 255, 255)
    NEON_PINK = (255, 20, 147)
    NEON_CYAN = (0, 255, 255)
    NEON_GREEN = (57, 255, 20)
    NEON_PURPLE = (155, 0, 255)
    NEON_YELLOW = (255, 255, 0)
    NEON_ORANGE = (255, 165, 0)
    DARK_PURPLE = (40, 0, 60)
    GLOW_BLUE = (100, 200, 255)

class PowerUpType(Enum):
    MULTI_BALL = 1
    SLOW_TIME = 2
    MEGA_BOUNCE = 3
    SHIELD = 4
    POINTS_2X = 5

class Particle:
    """Particle effect for visual enhancement"""
    def __init__(self, x, y, color, velocity=(0, 0)):
        self.x = x
        self.y = y
        self.vx = velocity[0] + random.uniform(-3, 3)
        self.vy = velocity[1] + random.uniform(-3, 3)
        self.color = color
        self.lifetime = 30
        self.size = random.randint(2, 6)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity effect
        self.lifetime -= 1
        self.size = max(1, self.size - 0.1)
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = min(255, self.lifetime * 8)
            color = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                             int(self.size))

class Ball:
    """Enhanced ball with trail effects and physics"""
    def __init__(self, x, y, color=Colors.NEON_CYAN):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = 0
        self.radius = BALL_RADIUS
        self.color = color
        self.trail = []
        self.max_trail_length = 10
        self.glowing = True
        self.bounce_count = 0
        
    def update(self, slow_factor=1.0):
        # Apply physics
        self.vy += GRAVITY * slow_factor
        self.x += self.vx * slow_factor
        self.y += self.vy * slow_factor
        
        # Update trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
        # Boundary checking
        if self.x <= self.radius or self.x >= SCREEN_WIDTH - self.radius:
            self.vx = -self.vx * BOUNCE_DAMPING
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
            
        # Top boundary
        if self.y <= self.radius:
            self.vy = abs(self.vy) * BOUNCE_DAMPING
            self.y = self.radius
            
    def draw(self, screen):
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail))) if self.trail else 0
            trail_color = (*self.color, alpha)
            pygame.draw.circle(screen, self.color, (int(pos[0]), int(pos[1])), 
                             int(self.radius * (i / len(self.trail))))
        
        # Draw main ball with glow effect
        if self.glowing:
            for i in range(3):
                glow_radius = self.radius + (i * 4)
                glow_alpha = 50 - (i * 15)
                pygame.draw.circle(screen, (*self.color, glow_alpha), 
                                 (int(self.x), int(self.y)), glow_radius, 2)
        
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, Colors.WHITE, (int(self.x), int(self.y)), 
                          self.radius, 2)

class Paddle:
    """Player-controlled paddle with enhanced visuals"""
    def __init__(self):
        self.width = 120
        self.height = 15
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - 40
        self.speed = PADDLE_SPEED
        self.color = Colors.NEON_PINK
        self.has_shield = False
        self.shield_timer = 0
        
    def move_left(self):
        self.x = max(0, self.x - self.speed)
        
    def move_right(self):
        self.x = min(SCREEN_WIDTH - self.width, self.x + self.speed)
        
    def update(self):
        if self.shield_timer > 0:
            self.shield_timer -= 1
            if self.shield_timer == 0:
                self.has_shield = False
                
    def draw(self, screen):
        # Draw main paddle with gradient effect
        for i in range(self.height):
            color_fade = int(255 * (1 - i / self.height))
            pygame.draw.rect(screen, self.color, 
                           (self.x, self.y + i, self.width, 1))
        
        # Draw edges
        pygame.draw.rect(screen, Colors.WHITE, 
                        (self.x, self.y, self.width, self.height), 2)
        
        # Draw shield if active
        if self.has_shield:
            pygame.draw.rect(screen, Colors.NEON_GREEN,
                           (self.x - 5, self.y - 5, self.width + 10, self.height + 10), 3)

class PowerUp:
    """Collectible power-ups"""
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = power_type
        self.vy = 2
        self.collected = False
        self.rotation = 0
        
        # Set color based on type
        self.colors = {
            PowerUpType.MULTI_BALL: Colors.NEON_CYAN,
            PowerUpType.SLOW_TIME: Colors.NEON_PURPLE,
            PowerUpType.MEGA_BOUNCE: Colors.NEON_YELLOW,
            PowerUpType.SHIELD: Colors.NEON_GREEN,
            PowerUpType.POINTS_2X: Colors.NEON_ORANGE
        }
        self.color = self.colors.get(self.type, Colors.WHITE)
        
    def update(self):
        self.y += self.vy
        self.rotation += 5
        
    def draw(self, screen):
        # Create rotating effect
        points = []
        for i in range(4):
            angle = math.radians(self.rotation + i * 90)
            x = self.x + self.width // 2 + math.cos(angle) * 15
            y = self.y + self.height // 2 + math.sin(angle) * 15
            points.append((x, y))
        
        pygame.draw.polygon(screen, self.color, points)
        pygame.draw.polygon(screen, Colors.WHITE, points, 2)

class Obstacle:
    """Moving obstacles to avoid"""
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vx = speed
        self.color = Colors.NEON_PURPLE
        
    def update(self):
        self.x += self.vx
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.vx = -self.vx
            
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, Colors.WHITE, (self.x, self.y, self.width, self.height), 2)

class NeonBounceGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Bounce - Ultimate Ball Game")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        self.reset_game()
        
    def reset_game(self):
        self.paddle = Paddle()
        self.balls = [Ball(SCREEN_WIDTH // 2, 100)]
        self.particles = []
        self.power_ups = []
        self.obstacles = []
        
        self.score = 0
        self.level = 1
        self.lives = 3
        self.combo = 0
        self.max_combo = 0
        
        self.game_over = False
        self.paused = False
        self.slow_time = False
        self.slow_timer = 0
        self.points_multiplier = 1
        self.multiplier_timer = 0
        
        # Create initial obstacles
        self.spawn_obstacles()
        
    def spawn_obstacles(self):
        """Spawn obstacles based on level"""
        self.obstacles.clear()
        for i in range(min(self.level, 5)):
            x = random.randint(100, SCREEN_WIDTH - 150)
            y = random.randint(200, 400)
            width = random.randint(50, 100)
            speed = random.uniform(1, 3) * (1 + self.level * 0.1)
            self.obstacles.append(Obstacle(x, y, width, 10, speed))
            
    def spawn_power_up(self):
        """Randomly spawn power-ups"""
        if random.random() < 0.002:  # 0.2% chance per frame
            x = random.randint(50, SCREEN_WIDTH - 50)
            power_type = random.choice(list(PowerUpType))
            self.power_ups.append(PowerUp(x, -30, power_type))
            
    def handle_collision(self, ball, paddle):
        """Enhanced collision with paddle"""
        if (ball.y + ball.radius >= paddle.y and 
            ball.y - ball.radius <= paddle.y + paddle.height and
            ball.x >= paddle.x and ball.x <= paddle.x + paddle.width):
            
            # Calculate bounce angle based on hit position
            hit_pos = (ball.x - paddle.x) / paddle.width
            bounce_angle = (hit_pos - 0.5) * math.pi / 3
            
            speed = math.sqrt(ball.vx**2 + ball.vy**2)
            ball.vx = speed * math.sin(bounce_angle)
            ball.vy = -abs(speed * math.cos(bounce_angle)) * 1.02  # Slight speed increase
            
            ball.bounce_count += 1
            self.combo += 1
            self.score += 10 * self.points_multiplier * (1 + self.combo // 5)
            
            # Create particle effects
            for _ in range(10):
                self.particles.append(
                    Particle(ball.x, ball.y, ball.color, (ball.vx/2, ball.vy/2))
                )
            
            return True
        return False
        
    def handle_obstacle_collision(self, ball, obstacle):
        """Handle ball collision with obstacles"""
        if (ball.x + ball.radius >= obstacle.x and 
            ball.x - ball.radius <= obstacle.x + obstacle.width and
            ball.y + ball.radius >= obstacle.y and
            ball.y - ball.radius <= obstacle.y + obstacle.height):
            
            # Determine bounce direction
            if ball.y < obstacle.y:
                ball.vy = -abs(ball.vy)
            elif ball.y > obstacle.y + obstacle.height:
                ball.vy = abs(ball.vy)
            else:
                ball.vx = -ball.vx
                
            # Lose combo
            self.combo = 0
            
            # Create particle effect
            for _ in range(5):
                self.particles.append(
                    Particle(ball.x, ball.y, Colors.NEON_PURPLE, (ball.vx/3, ball.vy/3))
                )
            
    def activate_power_up(self, power_type):
        """Activate collected power-up"""
        if power_type == PowerUpType.MULTI_BALL:
            # Add 2 extra balls
            for _ in range(2):
                new_ball = Ball(self.balls[0].x, self.balls[0].y, 
                              random.choice([Colors.NEON_CYAN, Colors.NEON_PINK, 
                                           Colors.NEON_GREEN]))
                self.balls.append(new_ball)
                
        elif power_type == PowerUpType.SLOW_TIME:
            self.slow_time = True
            self.slow_timer = 300  # 5 seconds at 60 FPS
            
        elif power_type == PowerUpType.MEGA_BOUNCE:
            for ball in self.balls:
                ball.vy = -20  # Super bounce
                
        elif power_type == PowerUpType.SHIELD:
            self.paddle.has_shield = True
            self.paddle.shield_timer = 600  # 10 seconds
            
        elif power_type == PowerUpType.POINTS_2X:
            self.points_multiplier = 2
            self.multiplier_timer = 450  # 7.5 seconds
            
    def update(self):
        """Main game update loop"""
        if self.game_over or self.paused:
            return
            
        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle.move_right()
            
        # Update paddle
        self.paddle.update()
        
        # Calculate slow factor
        slow_factor = 0.3 if self.slow_time else 1.0
        
        # Update balls
        balls_to_remove = []
        for ball in self.balls:
            ball.update(slow_factor)
            
            # Check paddle collision
            self.handle_collision(ball, self.paddle)
            
            # Check obstacle collisions
            for obstacle in self.obstacles:
                self.handle_obstacle_collision(ball, obstacle)
            
            # Check if ball fell off screen
            if ball.y > SCREEN_HEIGHT:
                balls_to_remove.append(ball)
                
        # Remove fallen balls
        for ball in balls_to_remove:
            self.balls.remove(ball)
            if not self.paddle.has_shield:
                self.lives -= 1
                self.combo = 0
            
            # Add new ball if all balls are gone
            if len(self.balls) == 0:
                if self.lives > 0:
                    self.balls.append(Ball(SCREEN_WIDTH // 2, 100))
                else:
                    self.game_over = True
                    
        # Update obstacles
        for obstacle in self.obstacles:
            obstacle.update()
            
        # Update power-ups
        self.spawn_power_up()
        power_ups_to_remove = []
        for power_up in self.power_ups:
            power_up.update()
            
            # Check collection
            if (power_up.y + power_up.height >= self.paddle.y and
                power_up.x + power_up.width >= self.paddle.x and
                power_up.x <= self.paddle.x + self.paddle.width):
                self.activate_power_up(power_up.type)
                power_ups_to_remove.append(power_up)
                self.score += 50 * self.points_multiplier
                
                # Create collection effect
                for _ in range(20):
                    self.particles.append(
                        Particle(power_up.x + 15, power_up.y + 15, power_up.color)
                    )
                    
            # Remove if off screen
            elif power_up.y > SCREEN_HEIGHT:
                power_ups_to_remove.append(power_up)
                
        for power_up in power_ups_to_remove:
            self.power_ups.remove(power_up)
            
        # Update particles
        particles_to_remove = []
        for particle in self.particles:
            particle.update()
            if particle.lifetime <= 0:
                particles_to_remove.append(particle)
                
        for particle in particles_to_remove:
            self.particles.remove(particle)
            
        # Update timers
        if self.slow_timer > 0:
            self.slow_timer -= 1
            if self.slow_timer == 0:
                self.slow_time = False
                
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer == 0:
                self.points_multiplier = 1
                
        # Update max combo
        self.max_combo = max(self.max_combo, self.combo)
        
        # Level progression
        if self.score > self.level * 1000:
            self.level += 1
            self.spawn_obstacles()
            
    def draw_background(self):
        """Draw animated background"""
        self.screen.fill(Colors.DARK_BG)
        
        # Draw grid pattern
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, Colors.DARK_PURPLE, (x, 0), 
                           (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, Colors.DARK_PURPLE, (0, y), 
                           (SCREEN_WIDTH, y), 1)
            
    def draw_ui(self):
        """Draw user interface elements"""
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, Colors.NEON_CYAN)
        self.screen.blit(score_text, (20, 20))
        
        # Level
        level_text = self.font_small.render(f"Level {self.level}", True, Colors.NEON_GREEN)
        self.screen.blit(level_text, (20, 60))
        
        # Lives
        for i in range(self.lives):
            pygame.draw.circle(self.screen, Colors.NEON_PINK, 
                             (SCREEN_WIDTH - 30 - i * 40, 30), 12)
            
        # Combo
        if self.combo > 0:
            combo_text = self.font_small.render(f"Combo x{self.combo}", True, 
                                               Colors.NEON_YELLOW)
            self.screen.blit(combo_text, (20, 90))
            
        # Power-up indicators
        if self.slow_time:
            slow_text = self.font_small.render("SLOW TIME", True, Colors.NEON_PURPLE)
            self.screen.blit(slow_text, (SCREEN_WIDTH // 2 - 50, 20))
            
        if self.points_multiplier > 1:
            multi_text = self.font_small.render(f"{self.points_multiplier}X POINTS", 
                                               True, Colors.NEON_ORANGE)
            self.screen.blit(multi_text, (SCREEN_WIDTH // 2 - 50, 50))
            
    def draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title_text = self.font_large.render("GAME OVER", True, Colors.NEON_PINK)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Stats
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, Colors.NEON_CYAN)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font_medium.render(f"Level Reached: {self.level}", True, Colors.NEON_GREEN)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(level_text, level_rect)
        
        combo_text = self.font_medium.render(f"Max Combo: {self.max_combo}", True, Colors.NEON_YELLOW)
        combo_rect = combo_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(combo_text, combo_rect)
        
        # Instructions
        restart_text = self.font_small.render("Press SPACE to play again or ESC to quit", 
                                             True, Colors.WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(restart_text, restart_rect)
        
    def draw_pause(self):
        """Draw pause screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(Colors.BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font_large.render("PAUSED", True, Colors.NEON_CYAN)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, pause_rect)
        
        continue_text = self.font_small.render("Press P to continue", True, Colors.WHITE)
        continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, 
                                                      SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(continue_text, continue_rect)
        
    def draw(self):
        """Main draw function"""
        self.draw_background()
        
        # Draw game elements
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
            
        for power_up in self.power_ups:
            power_up.draw(self.screen)
            
        for particle in self.particles:
            particle.draw(self.screen)
            
        for ball in self.balls:
            ball.draw(self.screen)
            
        self.paddle.draw(self.screen)
        
        self.draw_ui()
        
        if self.game_over:
            self.draw_game_over()
        elif self.paused:
            self.draw_pause()
            
    def run(self):
        """Main game loop"""
        running = True
        
        # Display start screen
        self.screen.fill(Colors.DARK_BG)
        title = self.font_large.render("NEON BOUNCE", True, Colors.NEON_CYAN)
        subtitle = self.font_medium.render("Press SPACE to Start", True, Colors.WHITE)
        controls = self.font_small.render("Controls: Arrow Keys or A/D to move, P to pause", 
                                         True, Colors.NEON_GREEN)
        
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 300))
        controls_rect = controls.get_rect(center=(SCREEN_WIDTH // 2, 400))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(controls, controls_rect)
        pygame.display.flip()
        
        # Wait for start
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        return
                        
        # Main game loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_p and not self.game_over:
                        self.paused = not self.paused
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
                        
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("NEON BOUNCE - Ultimate Bouncing Ball Game")
    print("=" * 60)
    print("\nGame Features:")
    print("- Multiple power-ups (Multi-ball, Slow Time, Shield, etc.)")
    print("- Dynamic obstacles and increasing difficulty")
    print("- Combo system for higher scores")
    print("- Stunning neon visual effects")
    print("- Particle effects and ball trails")
    print("\nControls:")
    print("- Arrow Keys or A/D: Move paddle")
    print("- P: Pause game")
    print("- SPACE: Start/Restart game")
    print("- ESC: Quit")
    print("\nPower-Ups:")
    print("- CYAN: Multi-ball - Spawns extra balls")
    print("- PURPLE: Slow Time - Slows down ball movement")
    print("- YELLOW: Mega Bounce - Super jump for all balls")
    print("- GREEN: Shield - Protects from losing lives")
    print("- ORANGE: 2X Points - Double score multiplier")
    print("\nStarting game...")
    print("=" * 60)
    
    game = NeonBounceGame()
    game.run()