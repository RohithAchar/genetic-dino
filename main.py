import pygame
import os
import random
from dataclasses import dataclass
pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
STATS_WIDTH = 500  # Width for stats panel on the right
TOTAL_WIDTH = SCREEN_WIDTH + STATS_WIDTH
SCREEN = pygame.display.set_mode((TOTAL_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Genetic Dino - Game + Stats")

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))


@dataclass
class DinoAgent:
    id: int
    gap_threshold: int          # when to jump
    duck_threshold: int         # when to duck (for birds)
    base_duck_duration: int     # how long (in frames) to stay ducking
    # parents that produced this agent (-1 means initial population)
    parent1_id: int = -1
    parent2_id: int = -1
    parent1_gap_threshold: int = 0
    parent1_duck_threshold: int = 0
    parent1_base_duck_duration: int = 0
    parent2_gap_threshold: int = 0
    parent2_duck_threshold: int = 0
    parent2_base_duck_duration: int = 0
    parent1_fitness: int = 0
    parent2_fitness: int = 0
    alive: bool = True
    color: tuple = (0, 0, 0)
    fitness: int = 0            # updated while running


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self, agent: DinoAgent):
        self.agent = agent
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        # how many frames to keep ducking (at 30 FPS, 30 ≈ 1s)
        self.duck_timer = 0

    def update(self, userInput, isJump, isDuck):
        # decrement existing duck timer
        if self.duck_timer > 0:
            self.duck_timer -= 1

        # If we're in a duck-timer window, stay ducking and ignore new jump/duck decisions
        if self.duck_timer > 0 and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        else:
            # Agent decisions take priority over keyboard
            if isJump and not self.dino_jump:
                # start jump, cancel other states
                self.dino_jump = True
                self.dino_duck = False
                self.dino_run = False
            elif isDuck and not self.dino_jump:
                # start duck using this dino's preferred duration (deterministic - no jitter)
                self.dino_duck = True
                self.dino_run = False
                self.dino_jump = False
                # Use exact base_duck_duration - fitness should be deterministic
                self.duck_timer = max(self.duck_timer, self.agent.base_duck_duration)
            else:
                # keyboard fallback
                if userInput[pygame.K_UP] and not self.dino_jump:
                    self.dino_jump = True
                    self.dino_duck = False
                    self.dino_run = False
                elif userInput[pygame.K_DOWN] and not self.dino_jump:
                    self.dino_duck = True
                    self.dino_run = False
                    self.dino_jump = False
                    # Use exact base_duck_duration - deterministic behavior
                    self.duck_timer = max(self.duck_timer, self.agent.base_duck_duration)
                elif not (self.dino_jump or userInput[pygame.K_DOWN]):
                    # default to running when no action
                    self.dino_duck = False
                    self.dino_run = True
                    self.dino_jump = False

        # Ensure mutually exclusive animation: jump > duck > run
        if self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.jump()
        elif self.dino_duck:
            self.dino_run = False
            self.duck()
        else:
            self.dino_duck = False
            self.dino_run = True
            self.run()

        if self.step_index >= 10:
            self.step_index = 0

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

    def distance(self):
        return self.rect.x


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index//5], self.rect)
        self.index += 1


def mutate_value(value, min_v, max_v, rate=0.25):
    """Mutate an integer value by up to ±12% with given probability."""
    if random.random() < rate:
        factor = 1 + random.uniform(-0.12, 0.12)  # ±12% mutation magnitude
        value = int(value * factor)
    return max(min_v, min(max_v, value))


def make_child(parent1: DinoAgent, parent2: DinoAgent, child_id: int) -> DinoAgent:
    """Create a mutated child agent from two parents (sexual reproduction)."""
    # Base genes are the arithmetic mean of the two parents' genes
    base_gap = (parent1.gap_threshold + parent2.gap_threshold) // 2
    base_duck = (parent1.duck_threshold + parent2.duck_threshold) // 2
    base_dur = (parent1.base_duck_duration + parent2.base_duck_duration) // 2

    return DinoAgent(
        id=child_id,
        gap_threshold=mutate_value(base_gap, 60, 300),
        duck_threshold=mutate_value(base_duck, 200, 300),  # Y position threshold (200-300)
        base_duck_duration=mutate_value(base_dur, 10, 80),
        parent1_id=parent1.id,
        parent2_id=parent2.id,
        parent1_gap_threshold=parent1.gap_threshold,
        parent1_duck_threshold=parent1.duck_threshold,
        parent1_base_duck_duration=parent1.base_duck_duration,
        parent2_gap_threshold=parent2.gap_threshold,
        parent2_duck_threshold=parent2.duck_threshold,
        parent2_base_duck_duration=parent2.base_duck_duration,
        parent1_fitness=parent1.fitness,
        parent2_fitness=parent2.fitness,
        alive=True,
        color=(
            random.randint(50, 255),
            random.randint(50, 255),
            random.randint(50, 255),
        ),
        fitness=0,
    )


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    # initial population
    generation = 1
    gen_history = []  # list of (gen_number, avg_fitness)
    best_fitness_history = []  # Track best fitness per generation for convergence detection
    CONVERGENCE_THRESHOLD = 0.05  # Stop if improvement < 5% over last 3 generations
    MAX_GENERATIONS = 50  # Safety limit
    # evaluate 20 dinos per generation, one at a time
    POP_SIZE = 100
    # For clarity in the UI, run 1 trial per dino (so dino index/score update immediately on death)
    NUM_TRIALS = 1  # games per dino, fitness = average points over these trials
    agents = [
        DinoAgent(
            id=i,
            # Initial values: reasonable but not optimal - allows room for evolution
            gap_threshold = random.randint(-200, 500),
            duck_threshold = random.randint(0, 500),
            base_duck_duration = random.randint(1, 40),

            color=(random.randint(10,255), random.randint(50,255), random.randint(50,255)),
        )
        for i in range(POP_SIZE)
    ]

    font = pygame.font.Font('freesansbold.ttf', 20)
    small_font = pygame.font.Font('freesansbold.ttf', 14)
    current_agent_index = {"idx": 0}  # mutable holder so inner function can see updates

    def draw_stats():
        """Draw all dino stats in the right panel"""
        # Clear stats area with light gray background
        stats_rect = pygame.Rect(SCREEN_WIDTH, 0, STATS_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(SCREEN, (240, 240, 240), stats_rect)
        
        # Draw border
        pygame.draw.line(SCREEN, (200, 200, 200), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        
        x_start = SCREEN_WIDTH + 10
        y = 20
        
        # Title
        title = font.render("Dino Stats", True, (0, 0, 0))
        SCREEN.blit(title, (x_start, y))
        y += 30
        
        # Dino count
        alive_count = sum(1 for agent in agents if agent.alive)
        dead_count = POP_SIZE - alive_count
        count_text = font.render(f"Alive: {alive_count} / Dead: {dead_count}", True, (0, 128, 0))
        SCREEN.blit(count_text, (x_start, y))
        y += 30
        
        # Sort agents by fitness
        sorted_agents_display = sorted(agents, key=lambda a: a.fitness, reverse=True)
        PARENT_POOL_SIZE = max(3, int(POP_SIZE * 0.35))
        ELITE_COUNT = 2
        
        # Show all dinos
        header = small_font.render("All Dinos (sorted by fitness):", True, (0, 0, 0))
        SCREEN.blit(header, (x_start, y))
        y += 20
        
        for idx, agent in enumerate(sorted_agents_display):
            # Determine color: elites (top 2), parents (top 35%), or normal
            if idx < ELITE_COUNT:
                text_color = (255, 200, 0) if agent.alive else (200, 150, 0)  # Gold
                prefix = "E"
            elif idx < PARENT_POOL_SIZE:
                text_color = (0, 100, 255) if agent.alive else (100, 150, 200)  # Blue
                prefix = "P"
            else:
                text_color = (0, 100, 0) if agent.alive else (150, 150, 150)  # Green/Gray
                prefix = ""
            
            # Compact format
            display_text = f"{prefix}{idx+1}. f:{int(agent.fitness)} g:{agent.gap_threshold} d:{agent.duck_threshold} t:{agent.base_duck_duration}"
            if not prefix:
                display_text = f"{idx+1}. f:{int(agent.fitness)} g:{agent.gap_threshold} d:{agent.duck_threshold} t:{agent.base_duck_duration}"
            
            dino_info = small_font.render(display_text, True, text_color)
            SCREEN.blit(dino_info, (x_start, y))
            y += 14
            
            # Stop if we run out of space
            if y > SCREEN_HEIGHT - 20:
                break

    def score():
        # Score display (points incremented in main loop now)
        text = font.render(f"Points: {points}", True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

        # Generation display
        gen_text = font.render(f"Gen: {generation}", True, (0, 0, 0))
        gen_rect = gen_text.get_rect()
        gen_rect.center = (1000, 70)
        SCREEN.blit(gen_text, gen_rect)

        # History display (recent generations)
        history_title = font.render("History", True, (0, 0, 0))
        SCREEN.blit(history_title, (SCREEN_WIDTH - 220, 110))

        recent = gen_history[-8:]  # show last 8 lines
        for idx_h, (gen_num, best_fit) in enumerate(recent):
            line = font.render(f"Gen{gen_num} - {best_fit}", True, (0, 0, 128))
            SCREEN.blit(line, (SCREEN_WIDTH - 220, 140 + idx_h * 22))

        # Dino count display
        alive_count = sum(1 for agent in agents if agent.alive)
        dead_count = POP_SIZE - alive_count
        status_text = font.render(f"Alive: {alive_count} / Dead: {dead_count}", True, (0, 128, 0))
        SCREEN.blit(status_text, (20, 20))


    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while True:
        # === Evaluate all 20 dinos together in the same scenario ===
        # Reset all agents for this generation
        for agent in agents:
            agent.alive = True
            agent.fitness = 0

        # Create all 20 dinos
        players = [Dinosaur(agent) for agent in agents]
        
        # Set deterministic seed for this generation (same obstacles for all dinos)
        random.seed(1234 + generation * 1000)

        # Reset game state
        run = True
        clock = pygame.time.Clock()
        cloud = Cloud()
        game_speed = 20
        x_pos_bg = 0
        y_pos_bg = 380
        points = 0
        obstacles = []

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            # Fill only game area (left side) with white
            game_area = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            pygame.draw.rect(SCREEN, (255, 255, 255), game_area)
            userInput = pygame.key.get_pressed()

            # Spawn obstacles (shared for all dinos)
            if len(obstacles) == 0:
                if random.randint(0, 2) == 0:
                    obstacles.append(SmallCactus(SMALL_CACTUS))
                elif random.randint(0, 2) == 1:
                    obstacles.append(LargeCactus(LARGE_CACTUS))
                elif random.randint(0, 2) == 2:
                    obstacles.append(Bird(BIRD))

            # Draw and update obstacles (shared)
            next_obstacle = None
            for obstacle in obstacles:
                obstacle.draw(SCREEN)
                obstacle.update()
                # Track the closest obstacle ahead for decision making
                if next_obstacle is None or obstacle.rect.x < next_obstacle.rect.x:
                    next_obstacle = obstacle

            # Update all alive dinos (each uses its own genes to decide)
            for player in players:
                if not player.agent.alive:
                    continue

                # Each dino decides based on its own genes
                is_jump = False
                is_duck = False
                if next_obstacle:
                    distance_diff = next_obstacle.distance() - 160
                    
                    # Deterministic decision: no jitter - fitness should be deterministic per genome
                    # Check if obstacle is at gap_threshold distance (time to decide)
                    if player.agent.gap_threshold <= distance_diff <= player.agent.gap_threshold + 40:
                        # Make decision based on Y position
                        # Lower Y = bird (higher on screen) → duck
                        # Higher Y = ground (lower on screen) → jump
                        if next_obstacle.rect.y <= player.agent.duck_threshold:
                            is_duck = True  # Obstacle is low enough (bird) → duck
                        else:
                            is_jump = True  # Obstacle is too high (ground) → jump

                player.draw(SCREEN)
                player.update(userInput, is_jump, is_duck)

                # Update fitness while alive (all dinos see same points)
                if player.agent.alive:
                    player.agent.fitness = points

                # Check collision with any obstacle
                for obstacle in obstacles:
                    if player.dino_rect.colliderect(obstacle.rect):
                        player.agent.alive = False
                        break

            # Increment points (shared counter)
            points += 1
            if points % 100 == 0:
                game_speed += 1

            # End generation when all dinos are dead
            if all(not agent.alive for agent in agents):
                run = False

            background()

            cloud.draw(SCREEN)
            cloud.update()

            # Update HUD (points, gen, history, all dinos, etc.)
            score()
            
            # Draw stats in separate panel on the right
            draw_stats()

            clock.tick(30)
            pygame.display.update()

        # Brief pause before next generation
        pygame.time.delay(500)

        # === Evolution step: build next generation from this generation's parents ===
        sorted_agents = sorted(agents, key=lambda a: a.fitness, reverse=True)
        # average fitness for this generation
        if sorted_agents:
            avg_fitness = sum(a.fitness for a in sorted_agents) / len(sorted_agents)
        else:
            avg_fitness = 0.0

        # record this generation's average score (for the history UI and logs)
        gen_history.append((generation, int(avg_fitness)))
        gen_min = min(a.fitness for a in sorted_agents) if sorted_agents else 0
        gen_max = max(a.fitness for a in sorted_agents) if sorted_agents else 0
        best_fitness = gen_max
        best_fitness_history.append(best_fitness)
        print(f"Gen {generation}: avg={avg_fitness:.1f}, min={gen_min:.1f}, max={gen_max:.1f}")
        
        # Check for convergence (minimal improvement over last 3 generations)
        converged = False
        if len(best_fitness_history) >= 4:
            recent_improvement = (best_fitness_history[-1] - best_fitness_history[-4]) / max(best_fitness_history[-4], 1)
            if recent_improvement < CONVERGENCE_THRESHOLD:
                converged = True
                print(f"\n⚠️  CONVERGENCE DETECTED!")
                print(f"   Improvement over last 3 generations: {recent_improvement*100:.2f}%")
                print(f"   Stopping evolution at generation {generation}\n")
        
        # Check max generations limit
        if generation >= MAX_GENERATIONS:
            print(f"\n⚠️  MAX GENERATIONS REACHED ({MAX_GENERATIONS})")
            print(f"   Stopping evolution\n")
            converged = True

        # select parents from *this* generation (top 35% = 7 out of 20)
        # Better diversity than top 3 - reduces genetic bottleneck
        PARENT_POOL_SIZE = max(3, int(POP_SIZE * 0.35))  # Top 35% as parent pool
        parent_pool = sorted_agents[:PARENT_POOL_SIZE]

        new_agents = []
        child_id = 0

        # Elitism: carry over top 2 unchanged
        ELITE = 2
        for elite in sorted_agents[:ELITE]:
            new_agents.append(
                DinoAgent(
                    id=child_id,
                    gap_threshold=int(elite.gap_threshold),
                    duck_threshold=int(elite.duck_threshold),
                    base_duck_duration=int(elite.base_duck_duration),
                    parent1_id=elite.parent1_id,
                    parent2_id=elite.parent2_id,
                    parent1_gap_threshold=elite.parent1_gap_threshold,
                    parent1_duck_threshold=elite.parent1_duck_threshold,
                    parent1_base_duck_duration=elite.parent1_base_duck_duration,
                    parent2_gap_threshold=elite.parent2_gap_threshold,
                    parent2_duck_threshold=elite.parent2_duck_threshold,
                    parent2_base_duck_duration=elite.parent2_base_duck_duration,
                    parent1_fitness=elite.parent1_fitness,
                    parent2_fitness=elite.parent2_fitness,
                    alive=True,
                    color=elite.color,
                    fitness=0,
                )
            )
            child_id += 1

        # Remaining slots: children from randomly sampled parent pairs
        # Random sampling from parent pool increases diversity
        while len(new_agents) < POP_SIZE:
            p1 = random.choice(parent_pool)
            p2 = random.choice(parent_pool)
            # Ensure parents are different
            while p1 == p2:
                p2 = random.choice(parent_pool)
            child = make_child(p1, p2, child_id)
            new_agents.append(child)
            child_id += 1

        agents = new_agents
        
        # Check if we should stop evolution
        if converged:
            # Display best result
            best_agent = sorted_agents[0]  # Already sorted by fitness
            print("\n" + "="*60)
            print("🏆 BEST RESULT FOUND!")
            print("="*60)
            print(f"Generation: {generation}")
            print(f"Best Fitness: {int(best_agent.fitness)}")
            print(f"\nBest Dino Genes:")
            print(f"  gap_threshold: {best_agent.gap_threshold}")
            print(f"  duck_threshold: {best_agent.duck_threshold}")
            print(f"  base_duck_duration: {best_agent.base_duck_duration}")
            print(f"\nGeneration Statistics:")
            print(f"  Average Fitness: {avg_fitness:.1f}")
            print(f"  Best Fitness: {gen_max:.1f}")
            print(f"  Worst Fitness: {gen_min:.1f}")
            print("="*60 + "\n")
            
            # Show on screen
            font_large = pygame.font.Font('freesansbold.ttf', 40)
            font_medium = pygame.font.Font('freesansbold.ttf', 24)
            
            # Clear and show best result
            SCREEN.fill((255, 255, 255))
            title = font_large.render("EVOLUTION COMPLETE!", True, (0, 150, 0))
            title_rect = title.get_rect()
            title_rect.center = (TOTAL_WIDTH // 2, 100)
            SCREEN.blit(title, title_rect)
            
            gen_text = font_medium.render(f"Final Generation: {generation}", True, (0, 0, 0))
            gen_rect = gen_text.get_rect()
            gen_rect.center = (TOTAL_WIDTH // 2, 160)
            SCREEN.blit(gen_text, gen_rect)
            
            fit_text = font_medium.render(f"Best Fitness: {int(best_agent.fitness)}", True, (0, 0, 0))
            fit_rect = fit_text.get_rect()
            fit_rect.center = (TOTAL_WIDTH // 2, 200)
            SCREEN.blit(fit_text, fit_rect)
            
            genes_title = font_medium.render("Best Genes:", True, (0, 0, 0))
            SCREEN.blit(genes_title, (TOTAL_WIDTH // 2 - 150, 250))
            
            gap_text = font.render(f"gap_threshold: {best_agent.gap_threshold}", True, (0, 0, 0))
            SCREEN.blit(gap_text, (TOTAL_WIDTH // 2 - 150, 290))
            
            duck_text = font.render(f"duck_threshold: {best_agent.duck_threshold}", True, (0, 0, 0))
            SCREEN.blit(duck_text, (TOTAL_WIDTH // 2 - 150, 320))
            
            dur_text = font.render(f"base_duck_duration: {best_agent.base_duck_duration}", True, (0, 0, 0))
            SCREEN.blit(dur_text, (TOTAL_WIDTH // 2 - 150, 350))
            
            stats_text = font.render(f"Avg: {avg_fitness:.1f} | Best: {gen_max:.1f} | Worst: {gen_min:.1f}", True, (0, 0, 0))
            SCREEN.blit(stats_text, (TOTAL_WIDTH // 2 - 200, 400))
            
            pygame.display.update()
            
            # Wait for user to close
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        return
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                        pygame.quit()
                        return
            
            break  # Exit the evolution loop
        
        generation += 1


def menu(death_count):
    global points
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any Key to Start", True, (0, 0, 0))
        elif death_count > 0:
            text = font.render("Press any Key to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 140))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                main()


main()
