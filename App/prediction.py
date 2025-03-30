import time
import cv2
import numpy as np
from App.model import UserMeet
from App.e import e_detect
from l2cs import Pipeline
import torch
from pathlib import Path
from collections import Counter
from deepface import DeepFace

# Initialize L2CS Gaze Detection Model
CWD = Path(__file__).resolve().parent

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print("Using device:", device)

gaze_pipeline = Pipeline(
    weights=CWD / 'L2CSNet_gaze360.pkl',
    arch='ResNet50',
    device=device
)

# Constants for Distance Estimation
KNOWN_FACE_HEIGHT = 170  # mm (average nose-to-chin distance)
FOCAL_LENGTH = 600  # Adjust based on your camera

# Thread Control
estimation_running = False

def detect_emotion(frame: np.ndarray):
    """Detect emotion using DeepFace."""
    try:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        analysis = DeepFace.analyze(frame_rgb, actions=["emotion"], enforce_detection=False)
        return analysis[0]["dominant_emotion"] if analysis else "Unknown"
    except Exception as e:
        print(f"DeepFace Error: {e}")
        return "Unknown"

def determine_engagement(gaze_point, image_width, image_height):
    """Determine engagement based on gaze point within the screen area."""
    engaged_zone = (
        int(image_width / 6),
        int(image_height / 6),
        int(image_width / 6 * 5),
        int(image_height / 6 * 5),
    )
    return "engaged" if engaged_zone[0] <= gaze_point[0] <= engaged_zone[2] and engaged_zone[1] <= gaze_point[1] <= engaged_zone[3] else "distracted"

def estimate_and_update_score(app, meeting_id, user_id, db):
    """Background function to estimate engagement and most frequent emotion every 10 seconds."""
    global estimation_running
    estimation_running = True
    cap = cv2.VideoCapture(0)
    count = 0
    score = 0
    total_count = 0
    total_score = 0
    emotion_counter = Counter()
    e_gad = 'Nothing'

    try:
        while estimation_running:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame")
                continue
            
            try:
                results = gaze_pipeline.step(frame)
                pitch, yaw = results.pitch[0], results.yaw[0]
                image_height, image_width = frame.shape[:2]
                face_box = results.bboxes[0]
                face_height = face_box[3] - face_box[1]
                
                if face_height <= 0:
                    print("Invalid face height detected")
                    continue

                distance_to_face = (KNOWN_FACE_HEIGHT * FOCAL_LENGTH) / face_height
                length_per_pixel = KNOWN_FACE_HEIGHT / face_height
                dx = -distance_to_face * np.tan(yaw) / length_per_pixel
                dy = -distance_to_face * np.tan(pitch) / length_per_pixel
                gaze_point = (int(image_width / 2 + dx), int(image_height / 2 + dy))
            except:
                print("No gaze detected")
                continue

            engagement_status = determine_engagement(gaze_point, image_width, image_height)
            print(engagement_status)
            detected_emotion = detect_emotion(frame)
            detected_gadget = e_detect(frame)
            if detected_gadget != 'No Gadget Found':
                e_gad = detected_gadget

            emotion_counter[detected_emotion] += 1
      
            if engagement_status == 'engaged':
                score += 1
                total_score += 1
                print(score ,  total_score)

            count += 1
            total_count += 1

            if count == 30:  # Update every 10 frames
                with app.app_context():
                    try:
                        meet = UserMeet.query.filter_by(user_id=user_id, meet_id=meeting_id).first()
                        if meet:
                            meet.l_score = (score / count) * 100
                            meet.score = (total_score / total_count) * 100
                            meet.emotion = emotion_counter.most_common(1)[0][0] if emotion_counter else "Unknown"
                            meet.e_gad = e_gad
                            db.session.commit()
                            print(f"DB Updated: Engagement Score={meet.l_score}, Emotion={meet.emotion}, Gadget={e_gad}")
                            score = 0
                            count = 0
                            emotion_counter.clear()
                        else:
                            print("Meeting not found!")
                    except Exception as e:
                        db.session.rollback()
                        print(f"Database Error: {e}")
                
            
            time.sleep(0.1)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released, tracking stopped.")