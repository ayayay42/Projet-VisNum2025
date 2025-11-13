import math
from collections import deque

_recent_gestures = deque(maxlen=5)

def get_direction_from_index(landmarks):
    if not landmarks or len(landmarks[0]) < 9:
        return None

    points = landmarks[0]  
    index_tip = points[8]
    index_mcp = points[5]

    dx = index_tip[0] - index_mcp[0]
    dy = index_tip[1] - index_mcp[1]
    angle = math.degrees(math.atan2(-dy, dx))

    if -45 <= angle <= 45:
        gesture = "LEFT" #"RIGHT"
    elif 45 < angle < 135:
        gesture = "UP"
    elif -135 < angle < -45:
        gesture = "DOWN"
    else:
        gesture = "RIGHT" #"LEFT"

    _recent_gestures.append(gesture)

    if len(_recent_gestures) < _recent_gestures.maxlen:
        return gesture  
    return max(set(_recent_gestures), key=_recent_gestures.count)

def detect_open_hand(landmarks):
    """
    Detect an open hand gesture:
    All fingers are extended (tips above their lower joints).
    """
    if not landmarks or len(landmarks[0]) < 21:
        return False

    pts = landmarks[0]

    tips = [4, 8, 12, 16, 20]
    pips = [2, 6, 10, 14, 18]

    extended_count = 0
    for tip, pip in zip(tips[1:], pips[1:]):  
        if pts[tip][1] < pts[pip][1]: 
            extended_count += 1

    thumb_tip = pts[4]
    thumb_ip = pts[3]
    wrist = pts[0]
    if abs(thumb_tip[0] - wrist[0]) > abs(thumb_ip[0] - wrist[0]):
        extended_count += 1

    return extended_count >= 4

def hand_present(landmarks, min_landmark_count=21):
    """
    Robust check whether a hand is present in the landmarks result.
    Returns True if landmarks looks like a real hand (has enough points and non-zero coords).
    """
    if not landmarks:
        return False
    first = landmarks[0]
    if not first or len(first) < min_landmark_count:
        return False
    # ensure at least one landmark has non-zero coords (filter out bogus all-zero outputs)
    for pt in first:
        try:
            x, y = pt[0], pt[1]
        except Exception:
            return False
        if (x, y) != (0, 0):
            return True
    return False

def detect_closed_fist(landmarks):
    """
    Detect a closed fist gesture:
    All fingers are folded (tips below their lower joints).
    """
    if not landmarks or len(landmarks[0]) < 21:
        return False

    pts = landmarks[0]

    tips = [4, 8, 12, 16, 20]
    pips = [2, 6, 10, 14, 18]

    folded_count = 0
    for tip, pip in zip(tips[1:], pips[1:]):  
        if pts[tip][1] > pts[pip][1]: 
            folded_count += 1

    thumb_tip = pts[4]
    thumb_ip = pts[3]
    wrist = pts[0]
    if abs(thumb_tip[0] - wrist[0]) < abs(thumb_ip[0] - wrist[0]):
        folded_count += 1

    return folded_count >= 4