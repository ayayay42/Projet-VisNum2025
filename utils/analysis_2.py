import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

df = pd.read_csv("logs/session_20251120_141424.csv")

# ======================================================
# 1. Sélection des frames réellement évaluables
# ======================================================

# Jeu actif : paused = 0 ET game_over = 0
df_active = df[(df["paused"] == 0) & (df["game_over"] == 0)]

# Tentative de restart : pause ou game_over peu importe, mais geste réel = RESTART
df_restart_attempt = df[(df["gesture_real"] == "RESTART")]

# Frames utiles = frames actives + frames de restart
df_eval = pd.concat([df_active, df_restart_attempt]).reset_index(drop=True)

print(f"Nombre de frames réellement analysées : {len(df_eval)}")

# ======================================================
# 2. Détection de main (uniquement quand frame analysée)
# ======================================================
hand_detection_rate = df_eval["hand_detected"].mean() * 100

# ======================================================
# 3. Accuracy des gestes
# ======================================================

y_true = df_eval["gesture_real"]
y_pred = df_eval["gesture_detected"].replace("NONE", "NO_GESTURE")

gesture_accuracy = (y_true == y_pred).mean() * 100

# ======================================================
# 4. Matrice de confusion
# ======================================================

labels = sorted(set(y_true) | set(y_pred))
cm = confusion_matrix(y_true, y_pred, labels=labels)

# ======================================================
# 5. Rapport détaillé
# ======================================================

report = classification_report(y_true, y_pred, labels=labels)

# ======================================================
# 6. Impression
# ======================================================

print("\n=== DETECTION DE MAIN ===")
print(f"Taux de détection de main (frames utiles) : {hand_detection_rate:.1f}%")

print("\n=== ACCURACY DES GESTES ===")
print(f"Précision globale des gestes : {gesture_accuracy:.1f}%")

print("\n=== CONFUSION MATRIX ===")
print("Labels :", labels)
print(cm)

print("\n=== RAPPORT PAR GESTE ===")
print(report)
