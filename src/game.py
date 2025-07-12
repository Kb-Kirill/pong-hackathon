import pygame
import os
from hand_tracker import HandTracker

# --- Настройки экрана ---
WIDTH, HEIGHT = 1200, 800

# --- Цвета ---
BG_COLOR = (30, 30, 30)
TABLE_COLOR = (70, 130, 180)  # Сине-голубой цвет стола
NET_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 0)
BUTTON_COLOR = (100, 100, 100)  # Серый для кнопок
BUTTON_TEXT_COLOR = (255, 255, 255)  # Белый текст на кнопках
SCORE_COLOR = (255, 255, 255)  # Белый для счёта

# --- Инициализация pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis Wall")
clock = pygame.time.Clock()

# --- Шрифт для текста ---
font = pygame.font.SysFont("arial", 40)  # Шрифт для счёта и кнопок

# --- Начальные позиции и состояние ---
ball_pos = [WIDTH // 2, HEIGHT // 3]
paddle_pos = [WIDTH // 2 - 30, HEIGHT - 140]  # x, y
score = 0  # Начальный счёт

# --- Загрузка изображения ракетки ---
script_dir = os.path.dirname(os.path.abspath(__file__))  # /Users/user/pong-hackathon/src
paddle_image_path = os.path.join(script_dir, "..", "assets", "image", "paddle.png")
paddle_image = pygame.image.load(paddle_image_path).convert_alpha()
paddle_image = pygame.transform.scale(paddle_image, (140, 140))

def draw_scene():
    screen.fill(BG_COLOR)

    # tracker = HandTracker(max_num_hands=1)
    # tracker.run()

    # Параметры для перспективы
    table_top_width = WIDTH * 0.2
    table_bottom_width = WIDTH * 0.9
    table_top_y = 250
    table_bottom_y = HEIGHT - int(0.2 * HEIGHT)

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

    # Центральная вертикальная линия стола
    pygame.draw.line(screen, NET_COLOR, (WIDTH // 2, table_top_y), (WIDTH // 2, table_bottom_y), 3)

    # Мяч
    pygame.draw.circle(screen, BALL_COLOR, ball_pos, 12)

    # Ракетка
    screen.blit(paddle_image, paddle_pos)

    # --- Счёт ---
    score_text = font.render(str(score), True, SCORE_COLOR)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 50))  # Центр сверху
    screen.blit(score_text, score_rect)

    # --- Кнопки ---
    # Кнопка "В меню"
    menu_button_rect = pygame.Rect(20, 20, 150, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, menu_button_rect)
    menu_text = font.render("В меню", True, BUTTON_TEXT_COLOR)
    menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
    screen.blit(menu_text, menu_text_rect)

    # Кнопка "Начать сначала"
    restart_button_rect = pygame.Rect(190, 20, 150, 50)
    pygame.draw.rect(screen, BUTTON_COLOR, restart_button_rect)
    restart_text = font.render("Начать", True, BUTTON_TEXT_COLOR)
    restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
    screen.blit(restart_text, restart_text_rect)

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
