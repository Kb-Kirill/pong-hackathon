import cv2
import pygame
import os
from hand_tracker import HandTracker
import random
import math
import time

random.seed(time.time())

# --- Настройки экрана ---
WIDTH, HEIGHT = 1200, 800

# --- Цвета ---
BG_COLOR = (30, 30, 30)
TABLE_COLOR = (1, 101, 163)  # Сине-голубой цвет стола
NET_COLOR = (255, 255, 255)
BALL_COLOR = (255, 255, 0)
BUTTON_COLOR = (175, 238, 27)  # Зеленый для кнопок
BUTTON_HOVER_COLOR = (45, 62, 71)  # Серый при наведении
BUTTON_TEXT_COLOR = (255, 255, 255)  # Белый текст на кнопках
SCORE_COLOR = (255, 255, 255)  # Белый для счёта
SHADOW_COLOR = (100, 100, 100)  # Серый для тени мяча
MIN_BALL_ANGLE = math.pi / 6  # 20 градусов (минимальный угол от горизонтали)
MAX_BALL_ANGLE = math.pi / 3  # 70 градусов (максимальный угол от горизонтали)
ball_top_y = 175  # Верхняя граница полёта мяча (выше стола)

WIN_COLOR = (0, 255, 0)  # Зеленый для победы
LOSE_COLOR = (255, 0, 0)  # Красный для поражения


# --- Инициализация pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis Wall")
clock = pygame.time.Clock()

# --- Шрифты ---
font_menu = pygame.font.SysFont("arial", 48)
font = pygame.font.SysFont("arial", 40)  # Шрифт для счёта и кнопок

pygame.mixer.init()

script_dir = os.path.dirname(os.path.abspath(__file__))

# --- Фоновая музыка ---
bg_music_path = os.path.join(script_dir, "..", "assets", "sound", "1.mp3")
pygame.mixer.music.load(bg_music_path)
pygame.mixer.music.set_volume(0.4)

# --- Звук удара (2.mp3) ---
hit_sound_path = os.path.join(script_dir, "..", "assets", "sound", "2.mp3")
hit_sound = pygame.mixer.Sound(hit_sound_path)
hit_sound.set_volume(0.4)

# --- Звук поражения (3.mp3) ---
hit_lose_path = os.path.join(script_dir, "..", "assets", "sound", "3.mp3")
hit_lose = pygame.mixer.Sound(hit_lose_path)
hit_lose.set_volume(0.4)             # при желании

# --- Звук поражения (4.mp3) ---
hit_win_path = os.path.join(script_dir, "..", "assets", "sound", "4.mp3")
hit_win = pygame.mixer.Sound(hit_win_path)
hit_win.set_volume(0.4)             # при желании

# --- Звук поражения 11w.mp3) ---
win_path = os.path.join(script_dir, "..", "assets", "sound", "11w.mp3")
win = pygame.mixer.Sound(win_path)
win.set_volume(0.4)             # при желании

# --- Звук поражения (11l.mp3) ---
lose_path = os.path.join(script_dir, "..", "assets", "sound", "11l.mp3")
lose = pygame.mixer.Sound(lose_path)
lose.set_volume(0.4)             # при желании

boss_flip_state = 0  # Состояние отзеркаливания: 0 (обычное), 1 (отзеркаленное)
boss_rotation_timer = 0  # Таймер для анимации отзеркаливания

# --- Параметры стола (глобальные) ---
table_top_width = WIDTH * 0.25  # Верхняя часть стола (узкая)
table_bottom_width = WIDTH * 0.6  # Нижняя часть стола
table_top_y = 250
table_bottom_y = HEIGHT - int(0.2 * HEIGHT)

# --- Начальные позиции и состояние ---
ball_pos = [WIDTH // 2, HEIGHT // 3]
ball_velocity = [5, 5]  # Начальная скорость мяча
ball_direction = 1  # 1: к противнику (вверх), -1: к игроку (вниз)
paddle_pos = [WIDTH // 2 - 70, HEIGHT - 140]  # x, y (смещено для центрирования ракетки)
player_score = 0  # Счёт игрока
opponent_score = 0  # Счёт стенки/противника
paddle_collision_cooldown = 0  # Таймер для задержки между столкновениями
wall_collision_cooldown = 0  # Таймер для задержки отскока от верхней границы
boss_x = WIDTH // 2 - 132 // 2  # Начальная позиция X босса (центр, с учётом ширины 132)
boss_flip_state = 0  # Состояние отзеркаливания: 0 (обычное), 1 (отзеркаленное)
boss_rotation_timer = 0  # Таймер для анимации отзеркаливания

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
ball_image = pygame.transform.scale(ball_image, (50, 50))  # Базовый размер мяча

# --- Загрузка фонового изображения для всего окна ---
background_image_path = os.path.join(script_dir, "..", "assets", "image", "background.jpg")
background_image = pygame.image.load(background_image_path).convert()
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

load_image_path = os.path.join(script_dir, "..", "assets", "image", "load_image.jpg")
load_image = pygame.image.load(load_image_path).convert()
load_image = pygame.transform.scale(load_image, (WIDTH, HEIGHT))

# --- Инициализация HandTracker ---
tracker = HandTracker(max_num_hands=1)
tracker.start_capture()

# --- Состояния игры ---
MENU = "menu"
GAME = "game"
game_state = MENU

def draw_menu():
    screen.blit(load_image, (0, 0))
    # Кнопка "Начать"
    button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 100)  # Было HEIGHT // 2
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, button_rect)

    # Текст кнопки
    text = font_menu.render("Начать", True, BUTTON_TEXT_COLOR)
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    if player_score >= 11:
        win_text = font_menu.render("ПОБЕДА!", True, WIN_COLOR)
        win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(win_text, win_rect)
        pygame.mixer.music.stop()
        win.play()
    elif opponent_score >= 11:
        lose_text = font_menu.render("ПОРАЖЕНИЕ", True, LOSE_COLOR)
        lose_rect = lose_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        screen.blit(lose_text, lose_rect)
        pygame.mixer.music.stop()
        lose.play()

def draw_scene(frame_surface=None):
    screen.blit(background_image, (0, 0))

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

    # --- Ножки стола ---
    leg_width = 20
    leg_color = (50, 50, 50)  # Тёмно-серый цвет ножек
    # Левая ножка
    left_leg_x = WIDTH // 2 - table_bottom_width // 2 + 100
    left_leg_y = table_bottom_y
    left_leg_height = HEIGHT - table_bottom_y
    pygame.draw.rect(screen, leg_color, (left_leg_x, left_leg_y, leg_width, left_leg_height))

    # Правая ножка
    right_leg_x = WIDTH // 2 + table_bottom_width // 2 - leg_width - 100
    right_leg_y = table_bottom_y
    right_leg_height = HEIGHT - table_bottom_y
    pygame.draw.rect(screen, leg_color, (right_leg_x, right_leg_y, leg_width, right_leg_height))

    # --- Второй игрок (boss) ---
    boss_width = 132
    boss_height = 200
    boss_y = table_top_y - boss_height
    boss_image_scaled = pygame.transform.scale(table_bg_image, (boss_width, boss_height))
    if boss_rotation_timer > 0:
        flipped_boss = pygame.transform.flip(boss_image_scaled, boss_flip_state == 1, False)
        screen.blit(flipped_boss, (boss_x, boss_y))
    else:
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
    # Параболическая интерполяция для Z: максимум у net_y, минимум у table_top_y и table_bottom_y
    distance_from_net = abs(ball_pos[1] - net_y)
    max_distance = max(net_y - table_top_y, table_bottom_y - net_y)
    z = 1 - (distance_from_net / max_distance) ** 2
    z = max(0, min(1, z))  # Ограничиваем Z в [0, 1]
    # Размер тени: от 30x20 (Z=0) до 15x10 (Z=1)
    shadow_width = int(30 - 15 * z)
    shadow_height = int(20 - 10 * z)
    # Смещение тени вниз: от 0 (Z=0) до 40 (Z=1)
    shadow_offset_y = int(40 * z)
    # Прозрачность тени: от 180 (Z=0) до 40 (Z=1)
    shadow_alpha = int(180 - 140 * z)
    # Создаём поверхность для тени
    if shadow_alpha > 0:  # Рисуем тень только если она видима
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (*SHADOW_COLOR, shadow_alpha), (0, 0, shadow_width, shadow_height))
        shadow_pos = (ball_pos[0] - shadow_width // 2, ball_pos[1] + shadow_offset_y - shadow_height // 2)
        screen.blit(shadow_surface, shadow_pos)

    # --- Мяч с текстурой и масштабированием ---
    z_ball = (table_bottom_y - ball_pos[1]) / (table_bottom_y - table_top_y)
    z_ball = max(0, min(1, z_ball))  # Ограничиваем Z в [0, 1]
    ball_scale = 50 - 20 * z_ball  # От 50x50 (Z=0) до 30x30 (Z=1)
    scaled_ball = pygame.transform.smoothscale(ball_image, (int(ball_scale), int(ball_scale)))
    ball_rect = scaled_ball.get_rect(center=ball_pos)
    screen.blit(scaled_ball, ball_rect)

    # --- Ракетка ---
    screen.blit(paddle_image, paddle_pos)

    # --- Счёт ---
    score_text = font.render(f"{player_score}:{opponent_score}", True, SCORE_COLOR)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(score_text, score_rect)

    # --- Кнопки ---
    menu_button_rect = pygame.Rect(20, 20, 150, 50)
    restart_button_rect = pygame.Rect(190, 20, 150, 50)
    mouse_pos = pygame.mouse.get_pos()
    if menu_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, menu_button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, menu_button_rect)
    menu_text = font.render("Меню", True, BUTTON_TEXT_COLOR)
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
                    ball_pos = [WIDTH // 2, ball_top_y + 100]  # Сброс позиции мяча
                    reset_angle = random.uniform(MIN_BALL_ANGLE, MAX_BALL_ANGLE)
                    speed = random.uniform(6, 8)
                    ball_velocity = [
                        speed * math.cos(reset_angle) * random.choice([-1, 1]),
                        speed * math.sin(reset_angle)
                    ]
                    ball_direction = 1  # Сброс направления (вверх)
                    boss_x = WIDTH // 2 - 132 // 2  # Сбрасываем позицию босса
            elif game_state == GAME:
                # Кнопки в игре
                pygame.mixer.music.play()
                menu_button_rect, restart_button_rect = draw_scene()
                if menu_button_rect.collidepoint(mouse_pos):
                    game_state = MENU  # Возврат в меню
                    boss_x = WIDTH // 2 - 132 // 2  # Сбрасываем позицию босса
                elif restart_button_rect.collidepoint(mouse_pos):
                    player_score = 0  # Сброс счёта игрока
                    opponent_score = 0  # Сброс счёта противника
                    ball_pos = [WIDTH // 2, ball_top_y + 100]  # Сброс позиции мяча
                    paddle_pos = [WIDTH // 2 - 70, HEIGHT - 140]  # Сброс позиции ракетки
                    reset_angle = random.uniform(MIN_BALL_ANGLE, MAX_BALL_ANGLE)
                    speed = random.uniform(6, 8)
                    ball_velocity = [
                        speed * math.cos(reset_angle) * random.choice([-1, 1]),
                        speed * math.sin(reset_angle)
                    ]
                    ball_direction = 1  # Сброс направления (вверх)
                    boss_x = WIDTH // 2 - 132 // 2  # Сбрасываем позицию босса

    # --- Обновление состояния ---
    if game_state == GAME:
        if player_score >= 11 or opponent_score >= 11:
            hit_sound.stop()
            hit_lose.stop()
            game_state = MENU
            boss_x = WIDTH // 2 - 132 // 2  # Сбрасываем позицию босса
        # Получаем координаты руки и кадр
        frame, coords = tracker.process_frame(draw_point=True)
        if frame is not None:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
            frame_surface = pygame.transform.scale(frame_surface, (320, 240))
        else:
            frame_surface = None

        if coords:
            x, y = coords
            paddle_pos[0] = int(x * WIDTH - 70)
            paddle_pos[1] = int(y * HEIGHT - 70)
            if (paddle_pos[1] < 350) or (paddle_pos[1] > 650) or (paddle_pos[0] < 100) or (paddle_pos[0] > 1000):
                paddle_image.set_alpha(120)
            else:
                paddle_image.set_alpha(255)
            paddle_pos[0] = max(0, min(paddle_pos[0], WIDTH - 140))

        # Обновление физики мяча
        ball_pos[0] += ball_velocity[0]
        ball_pos[1] += ball_velocity[1]

        # Обновление направления мяча
        ball_direction = -1 if ball_velocity[1] > 0 else 1

        # Уменьшаем таймер кулдауна
        if paddle_collision_cooldown > 0:
            paddle_collision_cooldown -= 1

        # Отскок от верхней границы (стенка)
        if ball_pos[1] <= ball_top_y and wall_collision_cooldown == 0:
            hit_sound.play()
            if abs(ball_velocity[1]) < 3:  # Если скорость слишком мала
                ball_velocity[1] = 8  # Устанавливаем достаточную скорость
            else:
                ball_velocity[1] = -ball_velocity[1] * 0.95
            ball_direction = -1  # Направление вниз после отскока
            boss_rotation_timer = 30  # ~0.5 сек при 60 FPS
            boss_flip_state = 1  # Начинаем с отзеркаленного состояния
            wall_collision_cooldown = 20  # ~0.33 сек при 60 FPS

        # Пропадание мяча за нижнюю границу
        if ball_pos[1] >= table_bottom_y:
            opponent_score += 1
            hit_lose.play()
            ball_pos = [WIDTH // 2, ball_top_y + 100]  # Сброс позиции дальше от верхней границы
            reset_angle = random.uniform(MIN_BALL_ANGLE, MAX_BALL_ANGLE)
            speed = random.uniform(6, 8)
            ball_velocity = [
                speed * math.cos(reset_angle) * random.choice([-1, 1]),
                speed * math.sin(reset_angle)
            ]
            ball_direction = 1  # Сброс направления (вверх)
            random.seed(time.time() + random.random())

        # Столкновение с ракеткой
        paddle_rect = pygame.Rect(paddle_pos[0], paddle_pos[1], 140, 140)
        collision_rect = paddle_rect.inflate(-paddle_rect.width // 2, -paddle_rect.height // 2)
        ball_rect = pygame.Rect(ball_pos[0] - 12, ball_pos[1] - 12, 24, 24)
        if collision_rect.colliderect(ball_rect) and paddle_collision_cooldown == 0 and paddle_image.get_alpha() == 255:
            hit_sound.play()
            relative_x = (ball_pos[0] - (paddle_pos[0] + 70)) / 70
            ball_velocity[0] = relative_x * 12
            ball_velocity[1] = -abs(ball_velocity[1]) * 1.2
            hit_win.play()
            # player_score += 1
            paddle_collision_cooldown = 20
            ball_direction = 1  # Направление вверх после удара

        # Обновление позиции босса по X
        if ball_direction == 1:  # Мяч движется к боссу
            target_x = ball_pos[0] - 136 // 2  # Цель: центр босса совпадает с мячом
            # Ограничиваем движение в пределах верхней части стола
            left_bound = WIDTH // 2 - table_top_width // 2
            right_bound = WIDTH // 2 + table_top_width // 2 - 132
            target_x = max(left_bound, min(right_bound, target_x))
            # Плавное движение (lerp)
            boss_x = boss_x * 0.9 + target_x * 0.1

        # Обновление анимации отзеркаливания оппонента
        if boss_rotation_timer > 0:
            if boss_rotation_timer % 10 == 0:
                boss_flip_state = 1 - boss_flip_state  # Чередуем 0 и 1
            boss_rotation_timer -= 1
            if boss_rotation_timer == 0:
                boss_flip_state = 0  # Возвращаем обычное состояние

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