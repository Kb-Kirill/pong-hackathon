import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        # Инициализация Mediapipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.cap = None

    def start_capture(self):
        """Запускает захват видео с веб-камеры."""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Не удалось открыть веб-камеру")

    def stop_capture(self):
        """Останавливает захват и освобождает ресурсы."""
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        self.hands.close()

    def process_frame(self, draw_point=True):
        """
        Обрабатывает текущий кадр, возвращает нормализованные координаты центра ладони.
        Args:
            draw_point: bool, рисовать ли точку в центре ладони
        Returns:
            tuple: (frame, normalized_coords), где normalized_coords - (x, y) или None
        """
        if not self.cap or not self.cap.isOpened():
            return None, None

        ret, frame = self.cap.read()
        if not ret:
            return None, None

        # Конвертация BGR в RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Обработка кадра
        results = self.hands.process(frame_rgb)

        # Конвертация обратно в BGR для отображения
        frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        normalized_coords = None
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Рисуем landmarks на руке
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Получаем координаты центра ладони (landmark 0 - основание ладони)
                palm_center = hand_landmarks.landmark[0]
                h, w, _ = frame.shape
                cx = int(palm_center.x * w)
                cy = int(palm_center.y * h)

                # Рисуем точку в центре ладони, если требуется
                if draw_point:
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), -1)

                # Сохраняем нормализованные координаты
                normalized_coords = (palm_center.x, palm_center.y)

        return frame, normalized_coords

    def run(self):
        """Запускает основной цикл обработки с отображением окна."""
        self.start_capture()
        try:
            while self.cap.isOpened():
                frame, coords = self.process_frame()
                if frame is None:
                    break

                # Отображаем кадр
                cv2.imshow('Hand Tracker', frame)

                # Выводим координаты в консоль, если они есть
                if coords:
                    print(f"Normalized coords: x={coords[0]:.3f}, y={coords[1]:.3f}")

                # Выход по нажатию 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        finally:
            self.stop_capture()
