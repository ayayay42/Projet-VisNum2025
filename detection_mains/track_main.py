import cv2
import mediapipe as mp

class HandTracker:
    def __init__(self, max_hands=1):
        self.hands = mp.solutions.hands.Hands(
            max_num_hands=max_hands,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils

    def get_landmarks(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        landmarks = []

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                h, w, _ = frame.shape
                hand_points = []
                for lm in handLms.landmark:
                    hand_points.append((int(lm.x * w), int(lm.y * h)))
                landmarks.append(hand_points)
                self.mp_draw.draw_landmarks(frame, handLms, mp.solutions.hands.HAND_CONNECTIONS)
        return landmarks, frame

