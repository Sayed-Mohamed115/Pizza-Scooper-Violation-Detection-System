import cv2
import pika
import base64
import json
import numpy as np
import os
import websocket
from ultralytics import YOLO

# ================= CONFIG =================
MODEL_PATH = "yolo12m-v2.pt"
QUEUE = "frames"
WS_URL = "ws://127.0.0.1:8000/ws"
CONF = 0.4

# ROI كنسب مئوية (يتحول لاحقًا لإحداثيات فعلية)
ROI_PERCENT = {"x1": 0.1, "y1": 0.3, "x2": 0.8, "y2": 0.7}

SAVE_DIR = "violations"
os.makedirs(SAVE_DIR, exist_ok=True)
# =========================================

model = YOLO(MODEL_PATH)
print("Model classes:", model.names)

# WebSocket
ws = websocket.WebSocket()
ws.connect(WS_URL)
print("✅ Connected to Streaming Service")

# RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()
channel.queue_declare(queue=QUEUE)

violation_count = 0

def inside_roi(b, roi):
    x1,y1,x2,y2 = b
    return not (x2 < roi["x1"] or x1 > roi["x2"] or y2 < roi["y1"] or y1 > roi["y2"])

def intersects(a,b):
    ax1,ay1,ax2,ay2 = a
    bx1,by1,bx2,by2 = b
    return not (ax2<bx1 or ax1>bx2 or ay2<by1 or ay1>by2)

def callback(ch, method, properties, body):
    global violation_count

    data = json.loads(body)
    img = base64.b64decode(data["image"])
    frame = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)

    h_img, w_img, _ = frame.shape

    # تحويل ROI النسبي لإحداثيات فعلية
    ROI = {
        "x1": int(ROI_PERCENT["x1"] * w_img),
        "y1": int(ROI_PERCENT["y1"] * h_img),
        "x2": int(ROI_PERCENT["x2"] * w_img),
        "y2": int(ROI_PERCENT["y2"] * h_img)
    }

    results = model(frame, conf=CONF, verbose=False)

    boxes = []
    hands, scoopers, pizzas = [], [], []

    for r in results:
        for b in r.boxes:
            cls = int(b.cls[0])
            label = model.names[cls]

            # تصحيح الإحداثيات لتكون ضمن حدود الصورة
            x1 = max(0, min(w_img, int(b.xyxy[0][0])))
            y1 = max(0, min(h_img, int(b.xyxy[0][1])))
            x2 = max(0, min(w_img, int(b.xyxy[0][2])))
            y2 = max(0, min(h_img, int(b.xyxy[0][3])))

            boxes.append({
                "x1": x1, "y1": y1,
                "x2": x2, "y2": y2,
                "label": label
            })

            if label == "hand":
                hands.append((x1,y1,x2,y2))
            elif label == "scooper":
                scoopers.append((x1,y1,x2,y2))
            elif label == "pizza":
                pizzas.append((x1,y1,x2,y2))

    violation = False

    for h in hands:
        if inside_roi(h, ROI):
            used_scooper = any(intersects(h, s) for s in scoopers)
            if not used_scooper:
                if any(intersects(h, p) for p in pizzas):
                    violation = True

    if violation:
        violation_count += 1
        cv2.imwrite(f"{SAVE_DIR}/v_{violation_count}.jpg", frame)

    # ----- للتأكد من عرض الـ boxes والـ ROI على الصورة -----
    for b in boxes:
        cv2.rectangle(frame, (b["x1"], b["y1"]), (b["x2"], b["y2"]), (0,255,0), 2)
        cv2.putText(frame, b["label"], (b["x1"], b["y1"]-5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    cv2.rectangle(frame, (ROI["x1"], ROI["y1"]), (ROI["x2"], ROI["y2"]), (0,0,255), 2)
    cv2.imshow("Detection Test", frame)
    cv2.waitKey(1)
    # ------------------------------------------------------

    payload = {
        "frame": data["image"],
        "boxes": boxes,
        "roi": ROI,
        "violations": violation_count,
        "violation": violation
    }

    ws.send(json.dumps(payload))

channel.basic_consume(queue=QUEUE, on_message_callback=callback, auto_ack=True)
print("🟢 Detection Service running")
channel.start_consuming()
