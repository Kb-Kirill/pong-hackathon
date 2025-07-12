import pygame
import os
from hand_tracker import HandTracker


# --- Настройки экрана ---
WIDTH, HEIGHT = 1200, 800

# --- Цвета ---
BG_COLOR = (30, 30, 30)
TABLE_COLOR = (80, 200, 120)
NET_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 0)

# --- Инициализация pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis Wall")
clock = pygame.time.Clock()

# --- Начальные позиции ---
ball_pos = [WIDTH // 2, HEIGHT // 3]
paddle_pos = [WIDTH // 2 - 30, HEIGHT - 140]  # x, y

# --- Загрузка изображения ракетки ---
script_dir = os.path.dirname(os.path.abspath(__file__))  # /Users/user/pong-hackathon/src
paddle_image_path = os.path.join(script_dir, "..", "assets", "image", "paddle.png")
paddle_image = pygame.image.load(paddle_image_path).convert_alpha()
paddle_image = pygame.transform.scale(paddle_image, (140, 140))

def draw_scene():
    screen.fill(BG_COLOR)

    tracker = HandTracker(max_num_hands=1)
    tracker.run()

    # Параметры для перспективы
    table_top_width = WIDTH * 0.2
    table_bottom_width = WIDTH * 0.9
    table_top_y = 250
    table_bottom_y = HEIGHT - int(0.2 * HEIGHT)  # стол поднят примерно на 10%

    # Левая половина стола
    left_table_points = [
        (WIDTH // 2, table_top_y),
        (WIDTH // 2 - table_top_width // 2, table_top_y),
        (WIDTH // 2 - table_bottom_width // 2, table_bottom_y),
        (WIDTH // 2, table_bottom_y)
    ]
    pygame.draw.polygon(screen, TABLE_COLOR, left_table_points)

    # Правая половина стола
    right_table_points = [
        (WIDTH // 2, table_top_y),
        (WIDTH // 2 + table_top_width // 2, table_top_y),
        (WIDTH // 2 + table_bottom_width // 2, table_bottom_y),
        (WIDTH // 2, table_bottom_y)
    ]
    pygame.draw.polygon(screen, TABLE_COLOR, right_table_points)

    # Сетка
    pygame.draw.line(screen, NET_COLOR, (WIDTH // 2, table_top_y), (WIDTH // 2, table_bottom_y), 3)

    # Мяч
    pygame.draw.circle(screen, BALL_COLOR, ball_pos, 12)

    # Ракетка (через картинку)
    screen.blit(paddle_image, paddle_pos)

# --- Главный игровой цикл ---
running = True
while running:
    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Обновление состояния ---
    # пока пусто

    # --- Рендер ---
    draw_scene()
    pygame.display.set_caption(f"Table Tennis Wall - FPS: {clock.get_fps():.2f}")
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
