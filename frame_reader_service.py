import cv2
import pika
import base64
import time
import json

# =============================
# RabbitMQ Connection
# =============================
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost')
)
channel = connection.channel()

channel.queue_declare(queue='frames')

print("[Frame Reader] ✅ Connected to RabbitMQ")
print("[Frame Reader] ▶️ Service is running...")

# =============================
# Video Source
# =============================
cap = cv2.VideoCapture("Sah w b3dha ghalt (3).mp4")  # 0 = webcam | or replace with video path

if not cap.isOpened():
    print("[Frame Reader] ❌ Cannot open video source")
    exit()

frame_id = 0

# =============================
# Main Loop
# =============================
while True:
    ret, frame = cap.read()
    if not ret:
        print("[Frame Reader] ❌ Failed to read frame")
        break

    _, buffer = cv2.imencode('.jpg', frame)
    frame_bytes = base64.b64encode(buffer).decode('utf-8')

    message = {
        "frame_id": frame_id,
        "timestamp": time.time(),
        "frame": frame_bytes
    }

    channel.basic_publish(
        exchange='',
        routing_key='frames',
        body=json.dumps(message)
    )

    print(f"[Frame Reader] 📤 Sent frame {frame_id}")

    frame_id += 1
    time.sleep(0.05)  # ~20 FPS

cap.release()
connection.close()
