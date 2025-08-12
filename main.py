import pygame
import random

WIDTH, HEIGHT = 600,600 #window size
BLOCK_SIZE = 20 #size of snake and food blocks

pygame.font.init() #display text
score_font = pygame.font.SysFont("consolas", 20)  
title_font = pygame.font.SysFont("consolas", 50) 
start_font = pygame.font.SysFont("consolas", 40)   
score = 0

# color definition
WHITE = (255, 255, 255)
YELLOW = (255, 215, 0)
GREEN = (170, 255, 0)
ORANGE = (255, 140, 0)
BLACK = (0,0,0)
GREY = (200,200,200)

DIFFICULTIES = ["easy", "medium", "hard"]
difficulty_colors = {
    "easy": (0, 200, 0),
    "medium": (200, 200, 0),
    "hard": (200, 0, 0)
}
difficulty_speeds = {
    "easy": 200,
    "medium": 100,
    "hard": 50
}
difficulty_max_foods = {
    "easy": 3,
    "medium": 5,
    "hard": 7
}
difficulty_poison = {
    "easy": 1,
    "medium": 2,
    "hard": 5
}
# initialize pygame
pygame.init()

# setting up display
win = pygame.display.set_mode((WIDTH, HEIGHT))

# setting up clock
clock = pygame.time.Clock()

def draw_button(text, x, y, font, win, rect_color, text_color=BLACK, padding=10, fixed_width=None):
    btn_text = font.render(text, True, text_color)
    text_rect = btn_text.get_rect()
    
    width = fixed_width if fixed_width is not None else text_rect.width + 2 * padding
    height = text_rect.height + 2 * padding
    
    background_rect = pygame.Rect(x, y, width, height)
    
    # Center text horizontally inside the rectangle
    text_x = x + (width - text_rect.width) // 2
    text_y = y + padding
    
    pygame.draw.rect(win, rect_color, background_rect, border_radius=5)
    win.blit(btn_text, (text_x, text_y))
    
    return background_rect


def lighten_color(color, amount=0.5):
    # color: (r,g,b), amount: 0..1 (0 no change, 1 white)
    r, g, b = color
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return (r, g, b)

def start_menu():
    selected = None
    running = True

    btn_width = 120
    btn_height = 40  # approx height with padding
    spacing = 20
    num_buttons = len(DIFFICULTIES)
    total_width = num_buttons * btn_width + (num_buttons - 1) * spacing
    start_x = (WIDTH - total_width) // 2
    y_pos = 350

    while running:
        win.fill(WHITE)
        main_title = title_font.render("Snake Game", True, GREEN)
        win.blit(main_title, (WIDTH//2 - main_title.get_width()//2, 150))

        subtitle = score_font.render("Select Difficulty", True, BLACK)
        win.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 300))

        btns = {}
        mouse_pos = pygame.mouse.get_pos()

        for i, diff in enumerate(DIFFICULTIES):
            x_pos = start_x + i * (btn_width + spacing)
            color = difficulty_colors[diff] if selected == diff else BLACK
            rect_color = lighten_color(color)
            btns[diff] = draw_button(diff.capitalize(), x_pos, y_pos, score_font, win, rect_color=rect_color, text_color=color, fixed_width=btn_width)

        start_btn_x = (WIDTH - (btn_width+50)) // 2
        start_btn = draw_button("Start", start_btn_x, 450, start_font, win, rect_color=GREEN, padding=25)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                for diff, rect in btns.items():
                    if rect.collidepoint(event.pos):
                        selected = diff
                if start_btn.collidepoint(event.pos) and selected:
                    return selected

        pygame.display.update()
        clock.tick(30)


# snake and food initialization
snake_pos = [[WIDTH//2, HEIGHT//2]] #start in middle
snake_speed = [0, BLOCK_SIZE] #starts moving down

teleport_walls = True  # set this to True to enable wall teleporting

# maximum number of foods at once on screen

foods = []
def generate_food():
    while True:
        x = random.randint(0, (WIDTH - BLOCK_SIZE) // BLOCK_SIZE ) * BLOCK_SIZE
        y = random.randint(0, (HEIGHT - BLOCK_SIZE) // BLOCK_SIZE ) * BLOCK_SIZE
        pos = [x, y]

        # check that new food is on empty space
        if pos not in [f[0] for f in foods] and pos not in snake_pos:
            # 10% chance for GREAT food
            n = random.randint(1, 10)
            if n < difficulty_poison[difficulty]:
                food_type = "POISON"
            elif n == 10:
                food_type = "GREAT"
            else:
                food_type = "NORMAL"
            return (pos, food_type)

def draw_objects():
    win.fill(WHITE) #clear screen by filling with black
    for pos in snake_pos:
        pygame.draw.rect(win, GREEN, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
    current_time = pygame.time.get_ticks()

    for pos, ftype, spawn_time in foods:
        if current_time >= spawn_time:
            color = YELLOW if ftype == "NORMAL" else ORANGE if ftype == "GREAT" else (0, 0, 0)
            pygame.draw.rect(win, color, pygame.Rect(pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))
    # Render the score
    score_text = score_font.render(f"Score: {score}", True, (0,0,0))
    win.blit(score_text, (10, 10))  # draws the score on the top-left corner

def update_snake():
    global foods, score, MAX_FOOD
    current_time = pygame.time.get_ticks()
    new_head = [snake_pos[0][0] + snake_speed[0], snake_pos[0][1] + snake_speed[1]]
    
    if teleport_walls:
        # if the new head position is outside of the screen, wrap it to the other side
        if new_head[0] >= WIDTH:
            new_head[0] = 0
        elif new_head[0] < 0:
            new_head[0] = WIDTH - BLOCK_SIZE
        if new_head[1] >= HEIGHT:
            new_head[1] = 0
        elif new_head[1] < 0:
            new_head[1] = HEIGHT - BLOCK_SIZE

    ate_food = None
    for food in foods:
        if new_head == food[0]:
            ate_food = food
            break

    if ate_food:
        if ate_food[1] == "GREATER":
            score += 3
        elif ate_food[1] == "POISON":
            if len(snake_pos) == 1:
                game_over_screen()
                return
            score -=1
            snake_pos.pop() #shrink 1 extra segment
            snake_pos.pop()
        else:
            score += 1
        foods.remove(ate_food)
        pos, ftype = generate_food()
        foods.append((pos, ftype, current_time))
        
    else:
        snake_pos.pop()
    
    snake_pos.insert(0, new_head) # add the new head to the snake

    # Replace food older than 10 seconds
    for i, (pos, ftype, spawn_time) in enumerate(foods):
        if current_time - spawn_time > 10000:  # 10 seconds
            new_pos, new_type = generate_food()
            foods[i] = (new_pos, new_type, current_time)

# TOP 10 HIGHEST SCORES SAVED AND DISPLAYED AFTER PLAYING
import os

HIGHSCORE_FILE = "highscore.txt"

def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        return 0
    with open(HIGHSCORE_FILE, "r") as f:
        try:
            return int(f.read().strip())
        except ValueError:
            return 0

def save_highscore(score):
    highscore = load_highscore()
    if score > highscore:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))

def game_over():
    # game over when snake hits the boundaries or runs into itself
    if teleport_walls:
        return snake_pos[0] in snake_pos[1:]
    else:
        return snake_pos[0] in snake_pos[1:] or \
            snake_pos[0][0] > WIDTH - BLOCK_SIZE or \
            snake_pos[0][0] < 0 or \
            snake_pos[0][1] > HEIGHT - BLOCK_SIZE or \
            snake_pos[0][1] < 0

def game_over_screen():
    global score
    win.fill((0, 0, 0))

    # High score on screen
    highscore = load_highscore()
    high_score_font = pygame.font.SysFont("consolas", 20)
    high_score_text = high_score_font.render(f"High Score: {highscore}", True, WHITE)
    win.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - high_score_text.get_height() // 2 - 20))

    # Game over
    game_over_font = pygame.font.SysFont("consolas", 30)
    game_over_text = game_over_font.render(f"Game Over! Score: {score}", True, WHITE)
    win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2 - 60))
 
    # Play again button
    play_btn_x = WIDTH // 2 - 200
    play_again_font = pygame.font.SysFont("consolas", 30)
    button_rect = draw_button("Play again", play_btn_x, 400, play_again_font, win, rect_color=GREEN, padding=25)

    # Home Button
    home_font = pygame.font.SysFont("consolas", 30)
    home_x = WIDTH// 2 + 50
    home_rect = draw_button("Home", home_x, 400, home_font, win, rect_color=GREY, padding=25)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
                       # Click detection
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    run(difficulty)  # restart game
                    return
                elif home_rect.collidepoint(event.pos):
                    start_menu() #go back to start menu
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run(difficulty)  # replay the game
                    return
                elif event.key == pygame.K_q:
                    pygame.quit()  # quit the game
                    return

def run(difficulty):
    global snake_speed, snake_pos, foods, score, MAX_FOOD
    MAX_FOOD = difficulty_max_foods[difficulty]
    snake_pos = [[WIDTH//2, HEIGHT//2]]
    snake_speed = [0, BLOCK_SIZE]
    score = 0
    running = True

    global MOVE_INTERVAL 
    MOVE_INTERVAL = difficulty_speeds[difficulty]  # milliseconds between moves (e.g., 100ms = 10 moves per second), the snakes speed
    last_move_time = pygame.time.get_ticks()

    foods = []
    start_time = pygame.time.get_ticks()
    for i in range(MAX_FOOD):
        pos, ftype = generate_food()
        spawn_time = start_time + i * 3000  # each food spawns 3 seconds apart
        foods.append((pos, ftype, spawn_time))

    while running:
        current_time = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        keys = pygame.key.get_pressed()

        # make sure snake can only turn 90 degrees, not 180 at once
        # Check input every frame for responsiveness
        if keys[pygame.K_UP] and snake_speed[1] != BLOCK_SIZE:
            snake_speed = [0, -BLOCK_SIZE]
        elif keys[pygame.K_DOWN] and snake_speed[1] != -BLOCK_SIZE:
            snake_speed = [0, BLOCK_SIZE]
        elif keys[pygame.K_LEFT] and snake_speed[0] != BLOCK_SIZE:
            snake_speed = [-BLOCK_SIZE, 0]
        elif keys[pygame.K_RIGHT] and snake_speed[0] != -BLOCK_SIZE:
            snake_speed = [BLOCK_SIZE, 0]

        # Move snake only every MOVE_INTERVAL milliseconds
        if current_time - last_move_time > MOVE_INTERVAL:
            if game_over():
                save_highscore(score)
                game_over_screen()
                return
            update_snake()
            last_move_time = current_time

        draw_objects()
        pygame.display.update()

        clock.tick(30)  # limit the frame rate to 30 FPS

if __name__ == '__main__':
    difficulty = start_menu()
    if difficulty:
        print(f"Starting game at {difficulty} difficulty!")
        run(difficulty)
        # Here, call your game run() with difficulty, e.g. run(difficulty)
    else:
        print("Exited game.")
