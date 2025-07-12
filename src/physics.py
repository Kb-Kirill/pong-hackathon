import math
import random


'''
Ключевые особенности:
 - Упрощённая физика:
    - Гравитация влияет только на вертикальную ось (Z)
    - Отскоки обрабатываются инвертированием скорости с коэффициентом упругости
    - Добавлено сопротивление воздуха для реалистичности

  - Псевдо-3D эффект:
    - Метод get_screen_position() преобразует 3D координаты в 2D с учётом перспективы
    - Чем дальше мяч (меньше y), тем "выше" он отображается

  - Столкновения:
    - Сетка обрабатывается как зона в середине стола с ограничением по высоте
    - Удары о стол/стенку теряют часть энергии (bounce коэффициент)

  - Старт и сброс:
    При сбросе мяч получает случайный начальный удар в сторону стенки
'''



class BallPhysics:
    def __init__(self, table_width, table_height, net_height):
        """
        :param table_width: ширина стола (в пикселях/условных единицах)
        :param table_height: длина стола (от игрока до стенки)
        :param net_height: высота сетки (для проверки удара)
        """
        self.table_width = table_width
        self.table_height = table_height
        self.net_height = net_height
        
        # Параметры мяча (стартовая позиция и скорость)
        self.reset_ball()
        
        # Физические параметры
        self.gravity = 0.2  # "тяжесть" мяча
        self.drag = 0.99    # сопротивление воздуха
        self.bounce = 0.7   # упругость отскока
        
    def reset_ball(self):
        """Сброс мяча в начальное положение (случайный начальный удар)"""
        self.x = self.table_width / 2
        self.y = self.table_height - 50  # старт у игрока
        self.z = 0  # "высота" мяча (псевдо-3D)
        
        # Начальная скорость (случайный легкий удар к стенке)
        self.vx = random.uniform(-2, 2)
        self.vy = -random.uniform(8, 10)  # в сторону стены (отрицательное значение)
        self.vz = random.uniform(5, 7)
    
    def update(self, dt):
        """
        Обновление позиции мяча с учётом физики
        :param dt: время с прошлого обновления (для плавности)
        """
        # Применяем гравитацию к вертикальной скорости
        self.vz -= self.gravity
        
        # Движение мяча
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.z += self.vz * dt
        
        # Применяем сопротивление воздуха
        self.vx *= self.drag
        self.vy *= self.drag
        self.vz *= self.drag
        
        # Проверка столкновений
        self._check_collisions()
        
    def _check_collisions(self):
        """Обработка всех столкновений (стол, сетка, стенка)"""
        # Столкновение с левой/правой границей стола
        if self.x <= 0 or self.x >= self.table_width:
            self.vx = -self.vx * self.bounce
            self.x = max(0, min(self.table_width, self.x))
        
        # Столкновение с сеткой (посередине стола)
        net_pos = self.table_height * 0.5  # сетка на половине стола
        net_width = self.table_width * 0.1  # ширина сетки
        
        if (abs(self.y - net_pos) < net_width and 
            self.z < self.net_height and 
            (self.vx != 0 or self.vy != 0)):
            
            # Мяч ударился в сетку - отскок с потерей скорости
            self.vx *= -0.5
            self.vy *= -0.5
            self.vz *= 0.3
            return True  # Возвращаем True для звукового эффекта
        
        # Столкновение со стенкой (дальний край)
        if self.y <= 0:
            self.vy = -self.vy * self.bounce
            self.y = 0
            self.vz *= 0.8  # теряем немного энергии при ударе о стенку
        
        # Столкновение с "полом" (столом)
        # Для большей зрелищности добавьте:
        # if self.z <= 0:  # При ударе о стол
            # sparkle_effect(self.x, self.y)  # Визуальный эффект
        
        # В physics.py внутри _check_collisions():
        if self.z <= 0:
            self.z = 0
            # Модификатор от горизонтальной скорости
            bounce_power = abs(self.vz) * (1 + 0.3 * abs(self.vx)/10)
            self.vz = bounce_power * self.bounce
            
            if abs(self.vz) < 0.1:
                self.vz = 0
                
        return False
    
    def is_out(self):
        """Проверка, улетел ли мяч за пределы игровой зоны"""
        return (self.y > self.table_height * 1.2 or  # улетел за игрока
                abs(self.x - self.table_width/2) > self.table_width * 0.6 or  # вбок
                self.z > 50)  # слишком высоко
    
    def get_position(self):
        """Возвращает позицию мяча в формате (x, y, z)"""
        return (self.x, self.y, self.z)
    
    def get_screen_position(self, perspective_factor=0.5):
        """
        Преобразует 3D позицию в 2D координаты для отрисовки с псевдо-3D эффектом
        :param perspective_factor: сила перспективы (0-1)
        """
        # Чем дальше мяч (меньше y), тем выше он на экране (имитация 3D)
        screen_y = self.table_height - self.y - self.z * perspective_factor
        return (self.x, screen_y)
    
    # Для сетевого обмена
    def get_state(self):
        return (self.x, self.y, self.z, self.vx, self.vy, self.vz)
    
    def set_state(self, state):
        self.x, self.y, self.z, self.vx, self.vy, self.vz = state
