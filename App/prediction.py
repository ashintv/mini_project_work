import time
import base64
import cv2
import numpy as np
import requests
import os
from App.model import UserMeet, Meeting
from App.e import e_detect

# API Key for Gaze Detection
ROBOFLOW_API_KEY = "udBRXEL0G6FxQlZJFTIF"
if not ROBOFLOW_API_KEY:
    raise ValueError("ROBOFLOW_API_KEY is not set. Please set it in your environment variables.")

# API Endpoint
GAZE_DETECTION_URL = f"http://127.0.0.1:9001/gaze/gaze_detection?api_key={ROBOFLOW_API_KEY}"

# Constants for Distance Estimation
KNOWN_FACE_HEIGHT = 170  # mm (average nose-to-chin distance)
FOCAL_LENGTH = 600  # Adjust based on your camera

# Thread Control
estimation_running = False
from deepface import DeepFace

def detect_emotion(frame: np.ndarray):
    """Detect emotion using DeepFace and print the detected emotion."""
    try:
        # Convert frame to RGB (since OpenCV loads images in BGR format)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Perform emotion analysis
        analysis = DeepFace.analyze(frame_rgb, actions=["emotion"], enforce_detection=False)
        
        if isinstance(analysis, list) and len(analysis) > 0:
            detected_emotion = analysis[0]["dominant_emotion"]# Print the detected emotion
            return detected_emotion

        return "Unknown"

    except Exception as e:
        print(f"DeepFace Error: {e}")
        return "Unknown"

def detect_gazes(frame: np.ndarray):
    """Send frame to gaze detection API and return predictions."""
    img_encode = cv2.imencode(".jpg", frame)[1]
    img_base64 = base64.b64encode(img_encode)

    try:
        resp = requests.post(
            GAZE_DETECTION_URL,
            json={"api_key": ROBOFLOW_API_KEY, "image": {"type": "base64", "value": img_base64.decode("utf-8")}},
        )
        resp.raise_for_status()
        data = resp.json()

        if not data or "predictions" not in data[0]:
            print("No predictions received from API")
            return []

        return data[0]["predictions"]

    except requests.exceptions.RequestException as e:
        print(f"Error contacting the gaze detection API: {e}")
        return []

def determine_engagement(gaze_point, image_width, image_height):
    """Determine engagement based on gaze point within the screen area."""
    engaged_zone = (
        int(image_width / 6),
        int(image_height / 6),
        int(image_width / 6 * 5),
        int(image_height / 6 * 5),
    )
    return "engaged" if engaged_zone[0] <= gaze_point[0] <= engaged_zone[2] and engaged_zone[1] <= gaze_point[1] <= engaged_zone[3] else "distracted"

from collections import Counter

def estimate_and_update_score(app, meeting_id, user_id, db):
    """Background function to estimate engagement and most frequent emotion every 10 seconds."""
    global estimation_running
    estimation_running = True
    cap = cv2.VideoCapture(0)
    count = 0
    score = 0
    total_count = 0
    total_score = 0
    emotion_counter = Counter()  # Store frequency of emotions

    try:
        while estimation_running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                continue
            gazes = detect_gazes(frame)
            if not gazes:
                print("No gaze detected")
            else:
                gaze = gazes[0]
                image_height, image_width = frame.shape[:2]
                # Extract face height for distance calculation
                face_height = gaze["face"]["height"]
                distance_to_face = (KNOWN_FACE_HEIGHT * FOCAL_LENGTH) / face_height
                length_per_pixel = KNOWN_FACE_HEIGHT / face_height
                # Calculate gaze points
                dx = -distance_to_face * np.tan(gaze["yaw"]) / length_per_pixel
                dy = -distance_to_face * np.tan(gaze["pitch"]) / length_per_pixel
                dx = 0 if np.isnan(dx) else dx
                dy = 0 if np.isnan(dy) else dy
                gaze_point = int(image_width / 2 + dx), int(image_height / 2 + dy)
                # Determine engagement
                
                engagement_status = determine_engagement(gaze_point, image_width, image_height)
                detected_emotion = detect_emotion(frame)
                
                detected_gadget = e_detect(frame)
                if detected_gadget != 'No Gadget Found':
                    e_gad = detected_gadget
    
                
            
                emotion_counter[detected_emotion] += 1
                if engagement_status == 'engaged':
                    score += 1
                    total_score += 1
            
                # Track emotions

            count += 1
            total_count += 1
            if count == 10:  # Every 30 frames (~10 seconds if ~3 FPS)
                with app.app_context():
                    try:
                        meet = UserMeet.query.filter_by(user_id=user_id, meet_id=meeting_id).first()
                        if meet:
                            meet.l_score = (score // count) * 100  # Last segment engagement
                            meet.score = (total_score // total_count) * 100  # Compute new percentage
                            most_frequent_emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else "Unknown"
                         
                            meet.e_gad = e_gad if e_gad != None else 'Nothing'
                            meet.emotion = most_frequent_emotion
                            db.session.commit()
                            print(f"DB Updated: Engagement Score={meet.score}, Most Frequent Emotion={most_frequent_emotion}, {e_gad}")
                            score = 0  # Reset score for next batch
                            emotion_counter.clear()  # Reset emotion counter
                        else:
                            print("Meeting not found!")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Database Error: {e}")
                count = 0  # Reset frame counter
            time.sleep(0.1)

    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released, tracking stopped.")