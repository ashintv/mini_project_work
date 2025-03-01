
from deepface import DeepFace
import cv2
import time
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils
def process_emotion_gaze(socketio):
    camera = cv2.VideoCapture(0)
    """Continuously count people and send data via WebSocket."""
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        while True:
            success, frame = camera.read()
            if not success or frame is None:
                print("Error: Camera frame not available.")
                continue

            # Convert BGR to RGB (MediaPipe requires RGB input)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the frame for face detection
            results = face_detection.process(rgb_frame)

            # Count the number of faces
            face_count = len(results.detections) if results.detections else 0
            
            try:
                analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                emotion = analysis[0]['dominant_emotion']
            except:
                emotion = "No face detected"

            # Draw face bounding boxes
            if results.detections:
                for detection in results.detections:
                    mp_drawing.draw_detection(frame, detection)

            # Display the frame (macOS-friendly fix)
            #cv2.imshow("Person Counter", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Send face count data to the client
            
            socketio.emit('emotion_gaze_data', {'person_count': face_count , 'emotion': emotion})
            print(f"Emitting: {face_count} , emotion is {emotion}")
            time.sleep(1)
            

    camera.release()
    cv2.destroyAllWindows()