# evaluator.py
import csv
import time
import os

class Evaluator:
    def __init__(self, log_dir="logs", session_name=None):
        """
        Logger pour enregistrer les performances du système.
        Chaque frame contiendra :
          - timestamp
          - main détectée (0/1)
          - geste détecté par l'IA
          - geste réel (clavier)
          - pause (0/1)
          - game over (0/1)
        """
        os.makedirs(log_dir, exist_ok=True)
        if session_name is None:
            session_name = time.strftime("%Y%m%d_%H%M%S")

        self.file_path = os.path.join(log_dir, f"session_{session_name}.csv")

        # Écrit la ligne d'en-tête
        with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "hand_detected",
                "gesture_detected",
                "gesture_real",
                "paused",
                "game_over"
            ])

    def log_frame(self, hand_detected, gesture_detected, gesture_real, paused, game_over):
        """
        Ajoute une ligne au CSV.
        - hand_detected : 0/1
        - gesture_detected : geste IA
        - gesture_real : geste clavier (ou NONE)
        - paused : 0/1
        - game_over : 0/1
        """
        with open(self.file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(),
                int(hand_detected),
                gesture_detected if gesture_detected else "NONE",
                gesture_real if gesture_real else "NONE",
                int(paused),
                int(game_over)
            ])

    def get_path(self):
        return self.file_path
