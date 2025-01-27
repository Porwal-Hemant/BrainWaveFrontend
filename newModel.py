from ultralytics import YOLO
import cv2
import cvzone
import math
import time
import os

# Load models
gloves_model = YOLO("yolov8s_custom.pt")  # Model for detecting gloves
other_model = YOLO("best.pt")  # Model for other items

# Class names for other_model
classNames = ['Hardhat', 'Mask', 'NO-Hardhat', 'NO-Mask', 'NO-Safety Vest',
              'Person', 'Safety Cone', 'Safety Vest', 'machinery', 'vehicle', 'goggles']

# Set up video source
cap = cv2.VideoCapture("./Videos/ppe-3.mp4")
cap.set(3, 1280)
cap.set(4, 720)

# Ensure output directory exists
os.makedirs('WORKERS/NO_SAFETY', exist_ok=True)

# FPS calculation
prev_frame_time = 0

# Time for periodic safety checks
last_check_time = time.time()

if not cap.isOpened():
    print("Error: Video file could not be opened.")
    exit()

while True:
    success, frame = cap.read()

    if not success:
        print("End of video or failed to capture image")
        break

    # Run detection for gloves using gloves_model
    gloves_results = gloves_model.predict(frame, verbose=False)
    detected_gloves = []  # To track detected gloves
    for r in gloves_results:
        for box in r.boxes:
            class_name = gloves_model.names[int(box.cls)]  # Get class name
            if class_name == "Gloves":  # Only process gloves
                detected_gloves.append(class_name)
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.putText(frame, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

    # Run detection for other items using other_model
    other_results = other_model(frame, stream=True)
    for r in other_results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            w, h = x2 - x1, y2 - y1
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])

            # Draw bounding boxes and labels for other items
            cvzone.cornerRect(frame, (x1, y1, w, h))
            cvzone.putTextRect(frame, f'{classNames[cls]} {conf}',
                               (max(0, x1), max(35, y1)), scale=1, thickness=1)

    # Periodic safety check for missing gloves
    current_time = time.time()
    if current_time - last_check_time >= 15:
        if 'Gloves' not in detected_gloves:
            now = time.localtime()
            filename = f"WORKERS/NO_SAFETY/{now.tm_year}{now.tm_mon:02d}{now.tm_mday:02d}_{now.tm_hour:02d}{now.tm_min:02d}{now.tm_sec:02d}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Safety violation saved: {filename}")
        last_check_time = current_time

    # FPS calculation
    new_frame_time = time.time()
    if prev_frame_time != 0:
        fps = 1 / (new_frame_time - prev_frame_time)
        fps = int(fps)
        cvzone.putTextRect(frame, f'FPS: {fps}', (10, 50), scale=1, thickness=1)
    prev_frame_time = new_frame_time

    # Display the frame
    cv2.imshow("Image", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
