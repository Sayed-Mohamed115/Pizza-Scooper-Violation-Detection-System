<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <title>Detection Frontend</title>
    <style>
        body { background: #1e1e1e; color: white; font-family: sans-serif; text-align: center; }
        canvas { background: #333; margin-top: 20px; }
        button { margin: 5px; padding: 10px 15px; font-size: 16px; }
        #alert { color: red; font-weight: bold; font-size: 20px; }
    </style>
</head>
<body>
    <h1>Detection Frontend</h1>
    <div>
        <button id="playBtn">▶ تشغيل الفيديو</button>
        <button id="pauseBtn">⏸ إيقاف الفيديو</button>
        <button id="roiInc">تكبير ROI</button>
        <button id="roiDec">تصغير ROI</button>
    </div>
    <div id="alert"></div>
    <div>عدد المخالفات: <span id="violationCount">0</span></div>
    <canvas id="canvas" width="640" height="480"></canvas>

    <script>
        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        const playBtn = document.getElementById("playBtn");
        const pauseBtn = document.getElementById("pauseBtn");
        const roiInc = document.getElementById("roiInc");
        const roiDec = document.getElementById("roiDec");
        const alertDiv = document.getElementById("alert");
        const violationCountEl = document.getElementById("violationCount");

        let videoPlaying = true;
        let roi = {x1:50, y1:200, x2:500, y2:600};
        let ws;

        function connectWS() {
            ws = new WebSocket("ws://127.0.0.1:8000/ws");

            ws.onopen = () => console.log("🟢 Connected to WebSocket");
            ws.onmessage = (event) => {
                if(!videoPlaying) return;

                const data = JSON.parse(event.data);
                const img = new Image();
                img.onload = () => {
                    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

                    // رسم ROI
                    ctx.strokeStyle = 'blue';
                    ctx.lineWidth = 3;
                    ctx.strokeRect(roi.x1, roi.y1, roi.x2-roi.x1, roi.y2-roi.y1);

                    // رسم Bounding Boxes
                    data.boxes.forEach(box => {
                        ctx.strokeStyle = box.label === "hand" ? "yellow" :
                                         box.label === "scooper" ? "green" : "orange";
                        ctx.lineWidth = 2;
                        ctx.strokeRect(box.x1, box.y1, box.x2-box.x1, box.y2-box.y1);
                        ctx.fillStyle = ctx.strokeStyle;
                        ctx.font = "14px sans-serif";
                        ctx.fillText(box.label, box.x1, box.y1-5);
                    });

                    // تنبيه المخالفة
                    if(data.violation) {
                        alertDiv.textContent = "❌ مخالفة!";
                    } else {
                        alertDiv.textContent = "";
                    }

                    // تحديث عداد المخالفات
                    violationCountEl.textContent = data.violations;
                };
                img.src = "data:image/jpeg;base64," + data.frame;
            };

            ws.onclose = () => {
                console.log("⚠️ WebSocket disconnected, retry in 1s");
                setTimeout(connectWS, 1000);
            };
        }

        connectWS();

        // ======== أزرار التحكم ========
        playBtn.onclick = () => { videoPlaying = true; };
        pauseBtn.onclick = () => { videoPlaying = false; };
        roiInc.onclick = () => {
            roi.x1 -= 10; roi.y1 -= 10; roi.x2 += 10; roi.y2 += 10;
        };
        roiDec.onclick = () => {
            roi.x1 += 10; roi.y1 += 10; roi.x2 -= 10; roi.y2 -= 10;
        };
    </script>
</body>
</html>
