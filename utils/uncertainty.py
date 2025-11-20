import numpy as np

_prev_pts = None

def spatial_variance(landmarks):
    if not landmarks or len(landmarks[0]) < 21:
        return 999
    pts = np.array(landmarks[0])
    return float(np.var(pts))

def temporal_jitter(landmarks):
    global _prev_pts
    if not landmarks or len(landmarks[0]) < 21:
        _prev_pts = None
        return 999

    pts = np.array(landmarks[0])
    if _prev_pts is None:
        _prev_pts = pts
        return 0

    jitter = float(np.mean(np.linalg.norm(pts - _prev_pts, axis=1)))
    _prev_pts = pts
    return jitter

def compute_uncertainty(landmarks):
    """
    Combine plusieurs mesures pour produire un score global d'incertitude.
    Plus le score est haut → plus l'incertitude est grande.
    """
    sv = spatial_variance(landmarks)
    tj = temporal_jitter(landmarks)

    # Weighted sum (you can tune weights)
    return 0.6 * sv + 0.4 * tj
