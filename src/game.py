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

# --- Инициализация pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis Wall")
clock = pygame.time.Clock()

# --- Начальные позиции ---
ball_pos = [WIDTH // 2, HEIGHT // 3]
paddle_pos = [WIDTH // 2 - 30, HEIGHT - 140]  # x, y

# --- Загрузка изображения ракетки ---
paddle_image_path = os.path.join("assets", "image", "paddle.png")
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

    # --- Сетка ---
    # Смещаем сетку выше (на 30% от верхней части стола)
    net_y = table_top_y + int((table_bottom_y - table_top_y) * 0.3)
    # Рассчитываем ширину сетки, чтобы она соответствовала ширине стола на уровне net_y
    net_width = (table_top_width + (table_bottom_width - table_top_width) * (
        (net_y - table_top_y) / (table_bottom_y - table_top_y)
    )) * 1.2  # Увеличиваем ширину на 20%
    net_half_width = net_width // 2

    # Вертикальная стойка сетки (по центру)
    pygame.draw.line(screen, NET_COLOR, (WIDTH // 2, net_y - 25), (WIDTH // 2, net_y + 25), 3)

    # Квадраты сетки (имитация ячеек) на всю ширину
    for y in range(net_y - 25, net_y + 25, 6):
        for x in range(-int(net_half_width), int(net_half_width), 6):
            pygame.draw.rect(screen, NET_COLOR, (WIDTH // 2 + x, y, 2, 2))

    # Мяч
    pygame.draw.circle(screen, BALL_COLOR, ball_pos, 12)

    # Ракетка
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