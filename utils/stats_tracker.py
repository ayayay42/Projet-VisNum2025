import time
import csv
import matplotlib
matplotlib.use("Agg")   
import matplotlib.pyplot as plt



class StatsTracker:
    def __init__(self):
        self.total_frames = 0
        self.frames_with_hand = 0
        self.frames_without_hand = 0

        self.gesture_counts = {
            "UP": 0,
            "DOWN": 0,
            "LEFT": 0,
            "RIGHT": 0,
            "NONE": 0
        }

        self.latencies = []
        self.uncertainty_values = []
        self.uncertainty_by_gesture = {
            "UP": [],
            "DOWN": [],
            "LEFT": [],
            "RIGHT": [],
            "NONE": []
        }

        
        # timestamps pour graphe
        self.frame_times = []
    

    def frame_start(self):
        """Call at the beginning of each frame."""
        self.frame_time = time.time()

    def record_gesture(self, gesture, hand_present):
        """Record gesture and presence of hand."""
        self.total_frames += 1

        if hand_present:
            self.frames_with_hand += 1
        else:
            self.frames_without_hand += 1

        if gesture in self.gesture_counts:
            self.gesture_counts[gesture] += 1
        else:
            self.gesture_counts["NONE"] += 1

        # latency
        latency = (time.time() - self.frame_time) * 1000
        self.latencies.append(latency)

    
    def record_uncertainty(self, value, gesture):
        self.uncertainty_values.append(value)
        self.frame_times.append(len(self.frame_times))

        # Ajouter l'incertitude pour le geste courant,
        # et NaN pour les autres (important pour le plot)
        import math
        for g in self.uncertainty_by_gesture:
            if g == gesture:
                self.uncertainty_by_gesture[g].append(value)
            else:
                self.uncertainty_by_gesture[g].append(math.nan)


    def export_csv(self, filename="results_stats.csv"):
        """Export results to a CSV file."""
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)

            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Frames", self.total_frames])
            writer.writerow(["Frames With Hand", self.frames_with_hand])
            writer.writerow(["Frames Without Hand", self.frames_without_hand])

            for g, count in self.gesture_counts.items():
                writer.writerow([f"Gesture {g}", count])

            writer.writerow(["Average Latency (ms)", sum(self.latencies) / len(self.latencies)])
            writer.writerow(["Max Latency (ms)", max(self.latencies)])
            writer.writerow(["Min Latency (ms)", min(self.latencies)])
            
            writer.writerow(["Average Uncertainty", sum(self.uncertainty_values)/len(self.uncertainty_values)])

    def plot_uncertainty(self, filename="uncertainty_plot.png"):
        if len(self.uncertainty_values) < 2:
            print("Pas assez de données pour tracer le graphe.")
            return

        plt.figure(figsize=(14, 7))

        colors = {
            "UP": "blue",
            "DOWN": "red",
            "LEFT": "green",
            "RIGHT": "orange",
            "NONE": "gray"
        }

        for gesture, values in self.uncertainty_by_gesture.items():
            plt.plot(
                self.frame_times,
                values,
                label=f"Incertitude {gesture}",
                linewidth=1.5,
                alpha=0.85,
                color=colors.get(gesture, "black")
            )

        plt.xlabel("Temps (frames)")
        plt.ylabel("Incertitude")
        plt.title("Incertitude de MediaPipe par geste détecté")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        plt.savefig(filename)
        plt.close()

        print(f"Graphe multi-courbes sauvegardé : {filename}")
