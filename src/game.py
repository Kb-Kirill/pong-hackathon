import cv2
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
BUTTON_HOVER_COLOR = (150, 150, 150)  # Серый при наведении
BUTTON_TEXT_COLOR = (255, 255, 255)  # Белый текст на кнопках
SCORE_COLOR = (255, 255, 255)  # Белый для счёта

# --- Инициализация pygame ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Table Tennis Wall")
clock = pygame.time.Clock()

# --- Шрифты ---
font_menu = pygame.font.SysFont("arial", 48)
font = pygame.font.SysFont("arial", 40)  # Шрифт для счёта и кнопок

# --- Начальные позиции и состояние ---
ball_pos = [WIDTH // 2, HEIGHT // 3]
paddle_pos = [WIDTH // 2 - 70, HEIGHT - 140]  # x, y (смещено для центрирования ракетки)
score = 0  # Начальный счёт

# --- Загрузка изображения ракетки ---
script_dir = os.path.dirname(os.path.abspath(__file__))
paddle_image_path = os.path.join(script_dir, "..", "assets", "image", "paddle.png")
paddle_image = pygame.image.load(paddle_image_path).convert_alpha()
paddle_image = pygame.transform.scale(paddle_image, (140, 140))

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

    # Отображаем окно камеры справа сверху
    if frame_surface:
        camera_rect = pygame.Rect(WIDTH - 330, 10, 320, 240)  # 10 пикселей отступа от краев
        screen.blit(frame_surface, camera_rect)

    # Параметры для перспективы
    table_top_width = WIDTH * 0.25  # Верхняя часть стола (узкая)
    table_bottom_width = WIDTH * 0.6  # Нижняя часть стола (уменьшено с 0.9 до 0.6)
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
    net_y = table_top_y + int((table_bottom_y - table_top_y) * 0.38)
    # Рассчитываем ширину сетки, чтобы она соответствовала ширине стола на уровне net_y
    net_width = (table_top_width + (table_bottom_width - table_top_width) * (
            (net_y - table_top_y) / (table_bottom_y - table_top_y)
    )) * 1.07  # Увеличиваем ширину на 20%
    net_half_width = net_width // 2

    # Квадраты сетки (имитация ячеек) на всю ширину
    for y in range(net_y - 25, net_y + 25, 6):
        for x in range(-int(net_half_width), int(net_half_width), 6):
            pygame.draw.rect(screen, NET_COLOR, (WIDTH // 2 + x, y, 2, 2))

    # Мяч
    pygame.draw.circle(screen, BALL_COLOR, ball_pos, 12)

    # Ракетка
    screen.blit(paddle_image, paddle_pos)

    # --- Счёт ---
    score_text = font.render(str(score), True, SCORE_COLOR)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(score_text, score_rect)

    # --- Кнопки ---
    # Кнопка "В меню"
    menu_button_rect = pygame.Rect(20, 20, 150, 50)
    mouse_pos = pygame.mouse.get_pos()
    if menu_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, menu_button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, menu_button_rect)
    menu_text = font.render("В меню", True, BUTTON_TEXT_COLOR)
    menu_text_rect = menu_text.get_rect(center=menu_button_rect.center)
    screen.blit(menu_text, menu_text_rect)

    # Кнопка "Начать сначала"
    restart_button_rect = pygame.Rect(190, 20, 150, 50)
    if restart_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, restart_button_rect)
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, restart_button_rect)
    restart_text = font.render("Начать", True, BUTTON_TEXT_COLOR)
    restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
    screen.blit(restart_text, restart_text_rect)

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
                    score = 0  # Сбрасываем счёт при начале игры
            elif game_state == GAME:
                # Кнопки в игре
                menu_button_rect, restart_button_rect = draw_scene()
                if menu_button_rect.collidepoint(mouse_pos):
                    game_state = MENU  # Возврат в меню
                elif restart_button_rect.collidepoint(mouse_pos):
                    score = 0  # Сброс счёта
                    ball_pos = [WIDTH // 2, HEIGHT // 3]  # Сброс позиции мяча
                    paddle_pos = [WIDTH // 2 - 70, HEIGHT - 140]  # Сброс позиции ракетки

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
            if 350 <= paddle_pos[1] <= 650:
                 paddle_image.set_alpha(255)
            else:
                 paddle_image.set_alpha(128)
            # Ограничиваем движение ракетки по горизонтали
            paddle_pos[0] = max(0, min(paddle_pos[0], WIDTH - 140))

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