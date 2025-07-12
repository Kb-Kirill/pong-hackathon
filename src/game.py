import cv2
import pygame
import os
from hand_tracker import HandTracker
import random

# --- Настройки экрана ---
WIDTH, HEIGHT = 1200, 800

# --- Цвета ---
BG_COLOR = (30, 30, 30)
TABLE_COLOR = (70, 130, 180)  # Сине-голубой цвет стола
NET_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 0)
BUTTON_COLOR = (175, 238, 27)  # Зеленый для кнопок
BUTTON_HOVER_COLOR = (45, 62, 71)  # Серый при наведении
BUTTON_TEXT_COLOR = (255, 255, 255)  # Белый текст на кнопках
SCORE_COLOR = (255, 255, 255)  # Белый для счёта
SHADOW_COLOR = (100, 100, 100)  # Серый для тени мяча

# --- Инициализация pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis Wall")
clock = pygame.time.Clock()

# --- Шрифты ---
font_menu = pygame.font.SysFont("arial", 48)
font = pygame.font.SysFont("arial", 40)  # Шрифт для счёта и кнопок

# --- Фоновая музыка ---
script_dir = os.path.dirname(os.path.abspath(__file__))
music_path = os.path.join(script_dir, "..", "assets", "sound", "1.mp3")
pygame.mixer.init()
pygame.mixer.music.load(music_path)
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

# --- Параметры стола (глобальные) ---
table_top_width = WIDTH * 0.25  # Верхняя часть стола (узкая)
table_bottom_width = WIDTH * 0.6  # Нижняя часть стола
table_top_y = 250
table_bottom_y = HEIGHT - int(0.2 * HEIGHT)

# --- Начальные позиции и состояние ---
ball_pos = [WIDTH // 2, HEIGHT // 3]
ball_velocity = [5, 5]  # Начальная скорость мяча
paddle_pos = [WIDTH // 2 - 70, HEIGHT - 140]  # x, y (смещено для центрирования ракетки)
player_score = 0  # Счёт игрока
opponent_score = 0  # Счёт стенки/противника
paddle_collision_cooldown = 0  # Таймер для задержки между столкновениями

# --- Загрузка изображения ракетки ---
paddle_image_path = os.path.join(script_dir, "..", "assets", "image", "paddle.png")
paddle_image = pygame.image.load(paddle_image_path).convert_alpha()
paddle_image = pygame.transform.scale(paddle_image, (140, 140))

# --- Загрузка фонового изображения стола ---
table_bg_image_path = os.path.join(script_dir, "..", "assets", "image", "boss.png")
table_bg_image = pygame.image.load(table_bg_image_path).convert_alpha()

# --- Загрузка изображения мяча ---
ball_image_path = os.path.join(script_dir, "..", "assets", "image", "ball.png")
ball_image = pygame.image.load(ball_image_path).convert_alpha()
ball_image = pygame.transform.scale(ball_image, (50, 50))  # Под размер как был круг

# --- Инициализация HandTracker ---
tracker = HandTracker(max_num_hands=1)
tracker.start_capture()

# --- Состояния игры ---
MENU = "menu"
GAME = "game"
game_state = MENU

def draw_menu():
    screen.fill(BG_COLOR)
    # Кнопка "Начать"
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)

    # Текст кнопки
    text = font_menu.render("Начать", True, BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

def draw_scene(frame_surface=None):
    screen.fill(BG_COLOR)

    # Окно камеры
    if frame_surface:
        camera_rect = pygame.Rect(WIDTH - 330, 10, 320, 240)
        screen.blit(frame_surface, camera_rect)

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

    # Центральная линия
    pygame.draw.line(screen, NET_COLOR, (WIDTH // 2, table_top_y), (WIDTH // 2, table_bottom_y), 3)

    # --- Второй игрок (boss) ---
    boss_width = 132
    boss_height = 200
    boss_x = WIDTH // 2 - boss_width // 2
    boss_y = table_top_y - boss_height
    boss_image_scaled = pygame.transform.scale(table_bg_image, (boss_width, boss_height))
    screen.blit(boss_image_scaled, (boss_x, boss_y))

    # --- Сетка ---
    net_y = table_top_y + int((table_bottom_y - table_top_y) * 0.38)
    net_width = (table_top_width + (table_bottom_width - table_top_width) *
                 ((net_y - table_top_y) / (table_bottom_y - table_top_y))) * 1.07
    net_half_width = net_width // 2
    for y in range(net_y - 25, net_y + 25, 6):
        for x in range(-int(net_half_width), int(net_half_width), 6):
            pygame.draw.rect(screen, NET_COLOR, (WIDTH // 2 + x, y, 2, 2))

    # --- Тень мяча ---
    # Условная высота Z: 0 у table_bottom_y, 1 у table_top_y
    z = (table_bottom_y - ball_pos[1]) / (table_bottom_y - table_top_y)
    z = max(0, min(1, z))  # Ограничиваем Z в [0, 1]
    # Размер тени: от 30x20 (Z=0) до 15x10 (Z=1)
    shadow_width = int(30 - 15 * z)
    shadow_height = int(20 - 10 * z)
    # Смещение тени вниз: от 0 (Z=0) до 40 (Z=1)
    shadow_offset_y = int(40 * z)
    # Прозрачность тени: от 180 (Z=0) до 40 (Z=1)
    shadow_alpha = int(180 - 140 * z)
    # Создаём поверхность для тени
    shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surface, (*SHADOW_COLOR, shadow_alpha), (0, 0, shadow_width, shadow_height))
    shadow_pos = (ball_pos[0] - shadow_width // 2, ball_pos[1] + shadow_offset_y - shadow_height // 2)
    screen.blit(shadow_surface, shadow_pos)

    # Мяч с текстурой
    ball_rect = ball_image.get_rect(center=ball_pos)
    screen.blit(ball_image, ball_rect)

    # Ракетка
    screen.blit(paddle_image, paddle_pos)

    # Счёт
    score_text = font.render(f"{player_score}:{opponent_score}", True, SCORE_COLOR)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(score_text, score_rect)

    # Кнопки
    menu_button_rect = pygame.Rect(20, 20, 150, 50)
    restart_button_rect = pygame.Rect(190, 20, 150, 50)

    mouse_pos = pygame.mouse.get_pos()
    if menu_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, menu_button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, menu_button_rect)
    menu_text = font.render("В меню", True, BUTTON_TEXT_COLOR)
    screen.blit(menu_text, menu_button_rect.move(20, 5))

    if restart_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, restart_button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, restart_button_rect)
    restart_text = font.render("Начать", True, BUTTON_TEXT_COLOR)
    screen.blit(restart_text, restart_button_rect.move(15, 5))

    return menu_button_rect, restart_button_rect

# --- Главный игровой цикл ---
running = True
while running:
    # События
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if game_state == MENU:
                # Кнопка "Начать" в меню
                button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)
                if button_rect.collidepoint(mouse_pos):
                    game_state = GAME
                    player_score = 0  # Сбрасываем счёт игрока
                    opponent_score = 0  # Сбрасываем счёт противника
                    ball_pos = [WIDTH // 2, HEIGHT // 3]  # Сброс позиции мяча
                    ball_velocity = [random.choice([-5, 5]), 5]  # Сброс скорости
            elif game_state == GAME:
                # Кнопки в игре
                menu_button_rect, restart_button_rect = draw_scene()
                if menu_button_rect.collidepoint(mouse_pos):
                    game_state = MENU  # Возврат в меню
                elif restart_button_rect.collidepoint(mouse_pos):
                    player_score = 0  # Сброс счёта игрока
                    opponent_score = 0  # Сброс счёта противника
                    ball_pos = [WIDTH // 2, HEIGHT // 3]  # Сброс позиции мяча
                    paddle_pos = [WIDTH // 2 - 70, HEIGHT - 140]  # Сброс позиции ракетки
                    ball_velocity = [random.choice([-5, 5]), 5]  # Сброс скорости

    # --- Обновление состояния ---
    if game_state == GAME:
        # Получаем координаты руки и кадр
        frame, coords = tracker.process_frame(draw_point=True)  # Включаем точку для отображения на камере
        if frame is not None:
            # Конвертируем кадр OpenCV (BGR) в RGB и затем в текстуру Pygame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            # Масштабируем кадр до размера окна камеры (320x240)
            frame_surface = pygame.transform.scale(frame_surface, (320, 240))
        else:
            frame_surface = None

        if coords:
            x, y = coords
            # Переводим нормализованные координаты в позицию ракетки
            paddle_pos[0] = int(x * WIDTH - 70)  # Смещение на половину ширины ракетки
            paddle_pos[1] = int(y * HEIGHT - 70)
            if (paddle_pos[1] < 350) or (paddle_pos[1] > 650) or (paddle_pos[0] < 100) or (paddle_pos[0] > 1000):
                paddle_image.set_alpha(120)
            else:
                paddle_image.set_alpha(255)
            # Ограничиваем движение ракетки по горизонтали
            paddle_pos[0] = max(0, min(paddle_pos[0], WIDTH - 140))

        # Обновление физики мяча
        ball_pos[0] += ball_velocity[0]
        ball_pos[1] += ball_velocity[1]

        # Уменьшаем таймер кулдауна
        if paddle_collision_cooldown > 0:
            paddle_collision_cooldown -= 1

        # Отскок от боковых границ стола
        table_left = WIDTH // 2 - table_bottom_width // 2
        table_right = WIDTH // 2 + table_bottom_width // 2
        if ball_pos[0] <= table_left or ball_pos[0] >= table_right:
            ball_velocity[0] = -ball_velocity[0] * 0.9  # Затухание

        # Отскок от верхней границы (стенка)
        if ball_pos[1] <= table_top_y:
            if abs(ball_velocity[1]) < 3:  # Если скорость слишком мала
                ball_velocity[1] = 8  # Устанавливаем достаточную скорость
            else:
                ball_velocity[1] = -ball_velocity[1] * 0.95  # Меньшее затухание

        # Пропадание мяча за нижнюю границу
        if ball_pos[1] >= table_bottom_y:
            opponent_score += 1
            ball_pos = [WIDTH // 2, HEIGHT // 3]  # Сброс позиции
            ball_velocity = [random.choice([-5, 5]), 5]  # Сброс скорости

        # Столкновение с ракеткой
        paddle_rect = pygame.Rect(paddle_pos[0], paddle_pos[1], 140, 140)
        collision_rect = paddle_rect.inflate(-paddle_rect.width // 2, -paddle_rect.height // 2)  # Сужаем зону
        ball_rect = pygame.Rect(ball_pos[0] - 12, ball_pos[1] - 12, 24, 24)
        if collision_rect.colliderect(ball_rect) and paddle_collision_cooldown == 0:
            relative_x = (ball_pos[0] - (paddle_pos[0] + 70)) / 70
            ball_velocity[0] = relative_x * 12
            ball_velocity[1] = -abs(ball_velocity[1]) * 1.2  # Ускорение при ударе
            player_score += 1
            paddle_collision_cooldown = 20  # ~0.33 сек при 60 FPS

    # --- Рендер ---
    if game_state == MENU:
        draw_menu()
    else:
        draw_scene(frame_surface)

    pygame.display.set_caption(f"Table Tennis Wall - FPS: {clock.get_fps():.2f}")
    pygame.display.flip()
    clock.tick(60)

# --- Очистка ---
tracker.stop_capture()
pygame.quit()