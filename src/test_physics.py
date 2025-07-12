import unittest
import math
from physics import BallPhysics

class TestBallPhysics(unittest.TestCase):
    def setUp(self):
        """Инициализация объекта физики перед каждым тестом"""
        self.ball = BallPhysics(table_width=800, table_height=600, net_height=50)
    
    def print_ball_status(self, label=""):
        """Вспомогательный метод для вывода статуса мяча"""
        x, y, z = self.ball.get_position()
        print(f"{label}: Pos=({x:.1f}, {y:.1f}, {z:.1f}) | Velocity=({self.ball.vx:.1f}, {self.ball.vy:.1f}, {self.ball.vz:.1f})")

    def test_initial_state(self):
        """Тест начального положения мяча"""
        x, y, z = self.ball.get_position()
        self.assertAlmostEqual(x, 400, delta=0.1)
        self.assertAlmostEqual(y, 550, delta=0.1)
        self.assertEqual(z, 0)
        print("\nTest 1 - Initial Position:")
        self.print_ball_status("Start")

    def test_gravity_effect(self):
        """Тест влияния гравитации на мяч"""
        print("\nTest 2 - Gravity Effect:")
        self.ball.reset_ball()
        self.ball.vx, self.ball.vy, self.ball.vz = 0, 0, 5  # Задаём начальную вертикальную скорость
        
        for step in range(5):
            self.ball.update(0.1)
            self.print_ball_status(f"Step {step+1}")
        
        # Проверяем, что Z-координата уменьшается под действием гравитации
        self.assertLess(self.ball.vz, 5)
        self.assertLess(self.ball.z, 5 * 0.1 * 5)  # z = v0*t - (g*t²)/2

    # Вариант 1 - Тестируем базовую физику (без модификаторов):
    # Если хотите тестировать только базовую физику - используйте Вариант 1
    def test_bounce_off_table(self):
        """Тест отскока от стола (базовый случай)"""
        print("\nTest 3 - Table Bounce:")
        self.ball.reset_ball()
        self.ball.x, self.ball.y, self.ball.z = 400, 300, 0
        self.ball.vx, self.ball.vy, self.ball.vz = 0, 0, -4  # Только вертикальное движение
        
        self.print_ball_status("Before bounce")
        self.ball.update(0.1)
        self.print_ball_status("After bounce")
        
        # Проверяем только направление и примерный диапазон
        self.assertGreater(self.ball.vz, 0)
        self.assertAlmostEqual(self.ball.vz, 4 * self.ball.bounce, delta=0.5)
    
    # Вариант 2 - Тестируем продвинутую физику (с модификаторами):
    # Если тестируете продвинутую физику - используйте Вариант 2
    def test_bounce_off_table(self):
        """Тест отскока от стола (с учётом горизонтальной скорости)"""
        print("\nTest 3 - Table Bounce:")
        self.ball.reset_ball()
        self.ball.x, self.ball.y, self.ball.z = 400, 300, 0
        self.ball.vx, self.ball.vy, self.ball.vz = 2, 0, -4
        
        expected_bounce = abs(-4) * (1 + 0.3 * abs(2)/10) * self.ball.bounce
        
        self.print_ball_status("Before bounce")
        self.ball.update(0.1)
        self.print_ball_status("After bounce")
        
        self.assertGreater(self.ball.vz, 0)
        self.assertAlmostEqual(self.ball.vz, expected_bounce, delta=0.1)
        
        self.assertAlmostEqual(self.ball.vz, expected_bounce, delta=0.1,
            msg=f"Expected vz ≈ {expected_bounce}, got {self.ball.vz}")
                    

    def test_net_collision(self):
        """Тест столкновения с сеткой"""
        print("\nTest 4 - Net Collision:")
        self.ball.reset_ball()
        net_pos = self.ball.table_height * 0.5
        self.ball.x, self.ball.y, self.ball.z = 400, net_pos, 30
        self.ball.vx, self.ball.vy, self.ball.vz = 5, 5, 0  # Летим в сетку
        
        self.print_ball_status("Before net hit")
        self.ball.update(0.1)
        self.print_ball_status("After net hit")
        
        # Скорости должны изменить направление и уменьшиться
        self.assertLess(abs(self.ball.vx), 5)
        self.assertLess(abs(self.ball.vy), 5)

    def test_pseudo_3d_projection(self):
        """Тест преобразования 3D в 2D координаты"""
        print("\nTest 5 - 3D Projection:")
        self.ball.reset_ball()
        self.ball.x, self.ball.y, self.ball.z = 400, 300, 20
        
        screen_x, screen_y = self.ball.get_screen_position()
        print(f"3D Position: (400, 300, 20) -> 2D Screen: ({screen_x:.1f}, {screen_y:.1f})")
        
        # Чем больше z и меньше y, тем выше на экране (меньше screen_y)
        self.assertLess(screen_y, 300)

    def test_out_of_bounds(self):
        """Тест выхода мяча за пределы"""
        print("\nTest 6 - Out of Bounds:")
        self.ball.reset_ball()
        self.ball.y = self.ball.table_height * 1.3  # Улетел за игрока
        
        self.assertTrue(self.ball.is_out())
        print("Ball is out (behind player) -", self.ball.get_position())

'''
Это позволит вам:
    Видеть как меняются координаты с каждым шагом
        Наблюдать эффекты гравитации и отскоков
        Проверять условия выхода мяча за пределы

Тесты покрывают:
    Начальное состояние
    Гравитацию
    Отскоки от стола и сетки
    Преобразование 3D→2D

Граничные условия
    Какие ещё аспекты физики вы хотели бы протестировать? Например, можно добавить тесты для:
    Ударов ракеткой (метод apply_hit())
    Разных углов отскока от стенок
    Эффектов вращения мяча
'''
def manual_test():
    """Ручной тест с пошаговой симуляцией"""
    ball = BallPhysics(800, 600, 50)
    ball.reset_ball()
    
    print("\nManual Test Mode (press Enter to step, 'q' to quit):")
    step = 0
    while True:
        step += 1
        ball.update(0.1)
        x, y = ball.get_screen_position()
        print(f"Step {step}: 2D Pos=({x:.1f}, {y:.1f}) | 3D Pos={ball.get_position()}")
        
        if ball.is_out():
            print("Ball is out of bounds!")
            ball.reset_ball()
        
        if input().lower() == 'q':
            break

if __name__ == "__main__":
    unittest.main(verbosity=2)
    #manual_test()  # Раскомментируйте для ручного теста








'''
from physics import BallPhysics

physics = BallPhysics(table_width=800, table_height=600, net_height=50)

while game_running:
    dt = clock.tick(60) / 1000.0  # дельта времени в секундах
    
    physics.update(dt)
    ball_pos = physics.get_screen_position()
    
    if physics.is_out():
        physics.reset_ball()
    
'''