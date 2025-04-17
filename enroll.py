# Author: Tumu Lakshman Prasanna Kumar
# Email: lpkumartumu@gmail.com
# GitHub: https://github.com/lakshman200309
# LinkedIn: https://www.linkedin.com/in/tumu-lakshman-prasanna-kumar-a37561270
# Portfolio: https://lakshman200309.github.io/Personal_Portfolio/

import cv2
import torch
import numpy as np
from facenet_pytorch import InceptionResnetV1
from ultralytics import YOLO
import time
import os

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

facenet_model = InceptionResnetV1(pretrained='vggface2').eval().to(device)
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

def enroll_user(user_id):
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    embeddings = []
    print("Show your face to the camera...")

    detected_once = False
    start_time = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        face = detect_face(frame)
        if face is not None:
            if not detected_once:
                print("✅ Face detected! Starting 1-minute capture...")
                start_time = time.time()
                detected_once = True

            if time.time() - start_time < 60:
                face_tensor = preprocess_face(face)
                with torch.no_grad():
                    embedding = facenet_model(face_tensor).cpu().numpy()
                embeddings.append(embedding[0])
            else:
                print("⏱️ 1 minute complete.")
                break

        cv2.imshow("Camera - Press Q to exit", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(embeddings) == 0:
        print("No face captured.")
        return

    mean_embedding = np.mean(np.array(embeddings), axis=0)

    if os.path.exists("face_embeddings.npy"):
        data = np.load("face_embeddings.npy", allow_pickle=True).item()
    else:
        data = {}

    data[user_id] = mean_embedding
    np.save("face_embeddings.npy", data)

    print(f"✅ Face enrolled for user ID: {user_id}")
