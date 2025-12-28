# Real-Time Violation Detection System

## 1. Project Overview

This project is a **real-time violation detection system** built using a **microservices architecture**.  
The system detects when a "hand" interacts with a "pizza" without using a "scooper" in a defined **Region of Interest (ROI)**.  

- The **Detection Service** runs a YOLOv8 object detection model to identify objects in video frames.  
- A **Frontend** UI displays the live video stream, detected objects (bounding boxes), ROI, and the count of violations in real-time.  
- Communication between services is handled via **RabbitMQ** (for frame transport) and **WebSocket** (for sending detection results to frontend).

This project is ideal for scenarios like **food safety monitoring** in restaurants or any controlled workspace where interactions need to be monitored.

---

## 2. Architecture Overview

Camera / Video Source
|
v
[Streaming Service] -> RabbitMQ -> [Detection Service] -> WebSocket -> [Frontend UI]


- **Detection Service:** Python microservice
  - Reads frames from RabbitMQ queue
  - Runs YOLOv8 object detection
  - Checks for violations in ROI
  - Sends processed frames + detection data to WebSocket server

- **Frontend UI:** Web-based interface
  - HTML + JavaScript Canvas
  - Displays video frames, bounding boxes, ROI
  - Shows count of violations
  - Controls: Start/Stop video, Show/Hide bounding boxes & ROI

---

## 3. Tools and Technologies Used

- **Programming Languages:**
  - Python 3.10+
  - JavaScript (Frontend)

- **Python Libraries:**
  - `ultralytics` (YOLOv8 model)
  - `opencv-python` (image/video processing)
  - `pika` (RabbitMQ communication)
  - `websocket-client` (WebSocket connection)
  - `numpy` (numerical operations)

- **Frontend:**
  - HTML5 + JavaScript
  - `<canvas>` for video rendering
  - Dynamic bounding boxes and ROI

- **Services/Servers:**
  - **RabbitMQ**: Message broker for sending frames
  - **WebSocket Server**: Real-time data transfer to frontend

- **Model:**
  - YOLOv8 (custom-trained `yolo12m-v2.pt`)

---

## 4. Setup and Installation

### 4.1 Install Python Dependencies
```bash
pip install ultralytics opencv-python pika websocket-client numpy

4.2 Install and Start RabbitMQ
https://www.rabbitmq.com/download.html
Start RabbitMQ server

4.3 Configure Detection Service

Place your YOLOv8 model (yolo12m-v2.pt) in the same directory as detection_service.py.

Adjust ROI percentages if needed (ROI_PERCENT in detection_service.py):

4.4 Run Frontend

Open index.html in a browser (Chrome recommended)

Click Start Video to connect to Detection Service

Use Toggle Bounding Boxes/ROI button to show/hide overlays

Use Stop Video to disconnect

5. Key Features

Real-time video streaming

Bounding boxes for detected objects

ROI overlay

Violation detection logic:

Hand interacts with pizza without scooper in ROI → violation incremented

Violation counter on UI

Interactive controls: Start/Stop stream, Show/Hide overlays

OpenCV preview for debugging frames and bounding boxes
