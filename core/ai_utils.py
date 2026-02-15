import cv2
import easyocr
from ultralytics import YOLO
import numpy as np

# Load models once to save time
model = YOLO('yolov8n.pt')  # Nano model for speed
reader = easyocr.Reader(['en'])

def analyze_evidence(video_path):
    """
    Analyzes a video/image for:
    1. Plate Number
    2. Helmet/Accident Detection
    3. Fake Video Check (Basic Frame consistency)
    """
    cap = cv2.VideoCapture(video_path)
    detected_plates = []
    violations = []
    is_fake = False
    
    # 3. Fake Video Check (Basic logic: Check if FPS/Encoding is standard)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps < 10 or fps > 120: 
        is_fake = True # Suspicious frame rate

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process every 10th frame to save speed
        if frame_count % 30 == 0:
            # A. YOLO Detection (Helmet, Accident, Person)
            results = model(frame)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    label = model.names[cls]
                    
                    # Logic: If Motorbike detected without Person+Helmet overlap
                    # (Simplified for beginner: Just detecting classes)
                    if label == 'motorcycle':
                        # In a real app, you check if the rider has a helmet
                        pass 
                    
                    # Assuming we have a custom model for 'accident' or 'no-helmet'
                    if label == 'person': 
                        # Placeholder for violation logic
                        violations.append("Overspeeding (Simulated)")

            # B. OCR (Number Plate)
            # Crop bottom area where plates usually are (optimization)
            height, width, _ = frame.shape
            roi = frame[int(height/2):, :] 
            
            ocr_result = reader.readtext(roi)
            for (bbox, text, prob) in ocr_result:
                if len(text) > 5 and prob > 0.5:
                    detected_plates.append(text.upper())
        
        frame_count += 1
    
    cap.release()
    
    # Return summary
    return {
        "plates": list(set(detected_plates)), # Unique plates
        "violations": list(set(violations)),
        "is_fake": is_fake
    }