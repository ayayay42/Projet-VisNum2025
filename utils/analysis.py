import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv("logs/session_20251120_141424.csv")

# ========== CLEANING ==========
# Remove frames where real gesture is NONE, unless you want to evaluate pauses
df_gestures = df[(df["gesture_real"] != "NONE") | (df["gesture_detected"] != "NONE")]

# ========== BASIC METRICS ==========

# Taux global de détection de main
hand_detection_rate = df["hand_detected"].mean() * 100

# Taux de détection quand le jeu n'est pas en pause
df_no_pause = df[df["paused"] == 0]
hand_detection_no_pause = df_no_pause["hand_detected"].mean() * 100

# Temps passé en pause
pause_ratio = df["paused"].mean() * 100

# Fréquence de gestes détectés
gesture_counts = df["gesture_detected"].value_counts()

# ========== GESTURE ACCURACY ==========

# Prendre uniquement les frames où un geste “réel” est défini (clavier)
df_valid = df[df["gesture_real"] != "NONE"]

y_true = df_valid["gesture_real"]
y_pred = df_valid["gesture_detected"].replace("NONE", "NO_GESTURE")

# Accuracy simple
gesture_accuracy = (y_true == y_pred).mean() * 100

# ========== CONFUSION MATRIX ==========
labels = sorted(set(y_true) | set(y_pred))

cm = confusion_matrix(y_true, y_pred, labels=labels)

# ========== CLASSIFICATION REPORT ==========
report = classification_report(y_true, y_pred, labels=labels)

# ========== PRINT RESULTS ==========

print("\n=== BASIC METRICS ===")
print(f"Taux de détection de la main : {hand_detection_rate:.1f}%")
print(f"Taux de détection (hors pause) : {hand_detection_no_pause:.1f}%")
print(f"Taux de pause : {pause_ratio:.1f}%")
print("\nDistribution des gestes détectés :")
print(gesture_counts)

print("\n=== GESTURE ACCURACY ===")
print(f"Précision globale des gestes : {gesture_accuracy:.1f}%")

print("\n=== CONFUSION MATRIX ===")
print("Labels :", labels)
print(cm)

print("\n=== DÉTAIL PAR GESTE (precision, recall, f1) ===")
print(report)
