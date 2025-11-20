import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load CSV
df = pd.read_csv("logs/session_20251119_145058.csv")

# Convert timestamp to relative time (seconds)
df["time"] = df["timestamp"] - df["timestamp"].iloc[0]

# -------------------------------------------
# 2. GESTURE FREQUENCY BAR PLOT
# -------------------------------------------
plt.figure(figsize=(8, 4))
sns.countplot(y=df["gesture_detected"], order=df["gesture_detected"].value_counts().index)
plt.title("Gesture Detection Frequency")
plt.xlabel("Count")
plt.ylabel("Gesture")
plt.savefig("plots/gesture_frequency.png")


plt.figure(figsize=(8, 4))
gesture_counts = df["gesture_detected"].value_counts()
gesture_percent = gesture_counts / gesture_counts.sum() * 100

sns.barplot(x=gesture_percent.values, y=gesture_percent.index)
plt.title("Gesture Detection Frequency (%)")
plt.xlabel("Percentage (%)")
plt.ylabel("Gesture")
plt.savefig("plots/gesture_frequency_percent.png")


# -------------------------------------------
# 3. CONFUSION MATRIX (gesture vs real gesture)
# → Works only if you logged real gestures in a column: gesture_real
# -------------------------------------------
if "gesture_real" in df.columns:
    from sklearn.metrics import confusion_matrix
    import numpy as np

    # Filter meaningful frames = while game is active
    usable = df[df["game_over"] == 0]

    cm = confusion_matrix(usable["gesture_real"], usable["gesture_detected"], labels=[
        "UP", "DOWN", "LEFT", "RIGHT", "NONE"
    ])

    cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100  # in percent
    
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_normalized, annot=True, fmt=".1f", cmap="Blues",
                xticklabels=["UP", "DOWN", "LEFT", "RIGHT", "NONE"],
                yticklabels=["UP", "DOWN", "LEFT", "RIGHT", "NONE"])
    plt.title("Confusion Matrix (Predicted vs Real Gestures)")
    plt.xlabel("Predicted Gesture")
    plt.ylabel("Real Gesture")
    plt.savefig("plots/confusion_matrix_normalized.png")
