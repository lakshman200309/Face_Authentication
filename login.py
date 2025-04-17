# Author: Tumu Lakshman Prasanna Kumar
# Email: lpkumartumu@gmail.com
# GitHub: https://github.com/lakshman200309
# LinkedIn: https://www.linkedin.com/in/tumu-lakshman-prasanna-kumar-a37561270
# Portfolio: https://lakshman200309.github.io/Personal_Portfolio/

import cv2
import torch
import numpy as np
import time
from scipy.spatial.distance import cosine
from facenet_pytorch import InceptionResnetV1
from ultralytics import YOLO
import os

# Initialize device and models
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
yolo_model = YOLO('yolov8n.pt').to(device)

def preprocess_face(face):
    face = cv2.resize(face, (160, 160))
    face = face.astype('float32') / 127.5 - 1
    face = np.transpose(face, (2, 0, 1))
    return torch.tensor(face).unsqueeze(0).to(device)

def detect_face(image):
    results = yolo_model(image)
    for result in results:
        for box in result.boxes:
            if int(box.cls[0]) == 0 and box.conf[0] > 0.5:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                return image[y1:y2, x1:x2]
    return None

def authenticate_face(threshold=0.3, max_duration=60):
    if not os.path.exists("face_embeddings.npy"):
        return "No registered faces found."

    data = np.load("face_embeddings.npy", allow_pickle=True).item()
    if not data:
        return "Face database is empty."

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Could not access the camera."

    embeddings = []
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        face = detect_face(frame)
        if face is not None:
            face_tensor = preprocess_face(face)
            with torch.no_grad():
                embedding = model(face_tensor).cpu().numpy()[0]
                embeddings.append(embedding)

            # Compute mean embedding and compare with saved data
            mean_embedding = np.mean(embeddings, axis=0)
            for user_id, stored_embedding in data.items():
                distance = cosine(mean_embedding, stored_embedding)
                if distance < threshold:
                    cap.release()
                    cv2.destroyAllWindows()
                    return f"Authenticated as ID: {user_id} (distance: {distance:.2f})"

        cv2.imshow("Authenticating... Press Q to cancel", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if time.time() - start_time > max_duration:
            break

    cap.release()
    cv2.destroyAllWindows()
    return "Face not recognized."
