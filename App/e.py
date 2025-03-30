import cv2
from ultralytics import YOLO

# Load the YOLOv8 model (pre-trained on COCO dataset)
model = YOLO("yolov8s.pt")
def e_detect(frame ):
    # Perform object detection
    results = model(frame,verbose=False)
    # Loop through detected objects
    for result in results:
        for box in result.boxes:
            conf = box.conf[0].item()  # Confidence score
            # Show only if confidence is greater than 80%
            if conf > 0.50:  # Get bounding box
                cls = int(box.cls[0].item())  # Class index
                label = model.names[cls]  # Class name
                if label in ["laptop", "cell phone", "remote"]:
                   return label
                else:
                    return 'No Gadget Found'

    
    # Display the framein
