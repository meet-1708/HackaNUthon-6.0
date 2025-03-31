# import cv2
# import torch
# from ultralytics import YOLO

# # Load the trained YOLO model
# model = YOLO('best_model.pt')  # Ensure this file exists in the same directory

# # Use GPU if available
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# model.to(device)

# # Open the webcam (try 0 or 1 if the default one doesn't work)
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Fix for Windows users

# if not cap.isOpened():
#     print("❌ Error: Could not access webcam")
#     exit()

# while True:
#     ret, frame = cap.read()
#     if not ret:
#         print("❌ Failed to capture image")
#         break
    
#     # Perform real-time inference
#     results = model(frame, verbose=False)  # Disable extra logs for speed

#     # Loop through detections and draw bounding boxes
#     for result in results:
#         for box in result.boxes.cpu().numpy():  # Convert to NumPy for processing
#             x1, y1, x2, y2 = map(int, box.xyxy[0])
#             label_id = int(box.cls[0])
#             label = result.names[label_id]  # Get the label name
#             confidence = box.conf[0].item()

#             # Draw bounding box and label
#             color = (0, 255, 0) if "Fresh" in label else (0, 0, 255)
#             cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#             cv2.putText(frame, f"{label} ({confidence:.2f})", (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

#     # Show the frame with real-time predictions
#     cv2.imshow('Fresh or Rotten Detector - Real Time', frame)

#     # Press 'q' to exit
#     if cv2.waitKey(7) & 0xFF == ord('q'):
#         break

# # Release resources
# cap.release()
# cv2.destroyAllWindows()
# print("✅ Webcam released successfully")

import cv2
import torch
import uvicorn
import base64
from fastapi import FastAPI
from ultralytics import YOLO
from fastapi.responses import StreamingResponse

# Initialize FastAPI app
app = FastAPI()

# Load the YOLO model
model = YOLO('best_model.pt')
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model.to(device)
print(model.names)

# Open the webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Function to process and return frames
def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Perform YOLO inference
        results = model.predict(frame, device=device, verbose=False)

        # Set confidence threshold (adjust as needed)
        CONFIDENCE_THRESHOLD = 0.73

        for result in results:
            for box in result.boxes:
                confidence = box.conf[0].item()
                label = result.names[int(box.cls[0])]

                if confidence < CONFIDENCE_THRESHOLD:
                    continue  # Skip low-confidence detections

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                color = (0, 255, 0) if "Fresh" in label else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, f"{label} ({confidence:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)


        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # Return frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# API Route to Stream Video
@app.get("/video_feed")
def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

# Run FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
