import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import numpy as np
from sklearn.metrics import confusion_matrix
import glob

filepaths = sorted(glob.glob("logs/spirale_*.csv"))

# Labels for consistency
GESTURES = ["UP", "DOWN", "LEFT", "RIGHT", "NONE"]

if len(filepaths) == 0:
    print("Aucun fichier spirale_*.csv trouvé dans logs/")
    sys.exit(1)

print("Fichiers détectés :")
for f in filepaths:
    print("  -", f)

all_freq_percent = []
all_conf_matrices = []

# ========== PROCESS ALL FILES ==========
for fp in filepaths:
    name = os.path.basename(fp)
    print(f"\n=== Processing {name} ===")

    df = pd.read_csv(fp)
    df["time"] = df["timestamp"] - df["timestamp"].iloc[0]

    # ---- Fréquence gestes ----
    freq = df["gesture_detected"].value_counts()
    freq_percent = (freq / freq.sum() * 100).reindex(GESTURES, fill_value=0)
    all_freq_percent.append(freq_percent.values)

    print("Frequencies (%):")
    print(freq_percent)

    # ---- Confusion matrix ----
    if "gesture_real" in df.columns:
        usable = df[df["game_over"] == 0]

        cm = confusion_matrix(
            usable["gesture_real"],
            usable["gesture_detected"],
            labels=GESTURES
        ).astype(float)

        row_sums = cm.sum(axis=1, keepdims=True)
        cm_norm = np.divide(cm, row_sums, out=np.zeros_like(cm),
                            where=row_sums != 0) * 100

        all_conf_matrices.append(cm_norm)

        print("Confusion Matrix Normalized (%):")
        print(pd.DataFrame(cm_norm, index=GESTURES, columns=GESTURES))

# ====== MOYENNES ======
mean_freq = np.mean(all_freq_percent, axis=0)
mean_cm = np.mean(all_conf_matrices, axis=0)

# ========== PLOTS ==========
# --- Mean gesture frequency ---
plt.figure(figsize=(8, 4))
sns.barplot(x=mean_freq, y=GESTURES)
plt.xlabel("Percentage (%)")
plt.ylabel("Gesture")
plt.title("Moyenne des fréquences de détection des gestes (%) - spirale")
os.makedirs("plots/percents", exist_ok=True)
plt.savefig("plots/percents/gesture_frequency_percent_MEAN.png")

# --- Mean confusion matrix ---
plt.figure(figsize=(6, 5))
sns.heatmap(mean_cm, annot=True, fmt=".1f", cmap="Blues",
            xticklabels=GESTURES, yticklabels=GESTURES)
plt.xlabel("Predicted")
plt.ylabel("Real")
plt.title("Matrice de confusion normalisée moyenne - spirale")
os.makedirs("plots/matrix", exist_ok=True)
plt.savefig("plots/matrix/confusion_matrix_normalized_MEAN.png")

# ====== SUMMARY PRINT ======
print("\n========== SUMMARY FOR REPORT ==========")
print("\nAverage Gesture Frequencies (%):")
for g, v in zip(GESTURES, mean_freq):
    print(f"{g:>5}: {v:.2f}%")

print("\nMean Normalized Confusion Matrix (%):")
print(pd.DataFrame(mean_cm, index=GESTURES, columns=GESTURES))