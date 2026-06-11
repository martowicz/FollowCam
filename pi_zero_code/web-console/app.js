const DEFAULT_TILT = 180;
const TILT_MIN = 120;
const TILT_MAX = 250;
const TILT_STEP = 10;
const TILT_STEP_AUTO = 2.5;
const TILT_MAX_STEP = 4;
const TILT_DEADZONE = 0.08;
const TILT_INVERT = 1;

const PAN_SPEED_MANUAL = 60;
const PAN_SPEED_MAX = 40;
const PAN_DEADZONE = 0.08;
const PAN_INVERT = 1;

const DETECT_MIN_SCORE = 0.6;
const DETECT_INTERVAL = 60;

const streamImg = document.getElementById("stream");
const overlay = document.getElementById("overlay");
const streamUrlLabel = document.getElementById("stream-url");
const statusEl = document.getElementById("status");
const visionStatusEl = document.getElementById("vision-status");
const trackingToggle = document.getElementById("toggle-tracking");
const panValueEl = document.getElementById("pan-value");
const tiltValueEl = document.getElementById("tilt-value");
const upBtn = document.getElementById("btn-up");
const leftBtn = document.getElementById("btn-left");
const rightBtn = document.getElementById("btn-right");
const downBtn = document.getElementById("btn-down");

const overlayCtx = overlay.getContext("2d");

let panSpeed = 0;
let tiltAngle = DEFAULT_TILT;
let socket = null;
let faceDetection = null;
let detectionReady = false;
let detectionBusy = false;
let lastDetectAt = 0;
let trackingEnabled = false;

streamImg.crossOrigin = "anonymous";

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const updateTelemetry = () => {
  panValueEl.textContent = String(Math.round(panSpeed));
  tiltValueEl.textContent = String(Math.round(tiltAngle));
};

const setStatus = (text, state) => {
  statusEl.textContent = text;
  statusEl.dataset.state = state;
};

const setVisionStatus = (text, state) => {
  visionStatusEl.textContent = text;
  visionStatusEl.dataset.state = state;
};

const setTrackingEnabled = (enabled) => {
  trackingEnabled = enabled;
  trackingToggle.setAttribute("aria-pressed", String(trackingEnabled));
  trackingToggle.textContent = trackingEnabled
    ? "Auto tracking: On"
    : "Auto tracking: Off";
  [upBtn, downBtn, leftBtn, rightBtn].forEach((btn) => {
    btn.disabled = trackingEnabled;
  });
  if (!trackingEnabled) {
    stopPan();
  }
};

const connectSocket = (host) => {
  if (typeof io === "undefined") {
    setStatus("Socket.io missing", "warn");
    return;
  }

  if (socket) {
    socket.disconnect();
  }

  setStatus("Connecting", "warn");
  socket = io(`http://${host}:5000`, {
    transports: ["websocket", "polling"],
  });

  socket.on("connect", () => setStatus("Connected", "ok"));
  socket.on("disconnect", () => setStatus("Disconnected", "off"));
  socket.on("connect_error", () => setStatus("Connect error", "warn"));
};

const connectToDevice = () => {
  const host = location.hostname;
  if (!host) {
    setStatus("Open via http://<pi-host>/", "warn");
    streamUrlLabel.textContent = "-";
    return;
  }

  const streamUrl = `http://${host}:8080/stream`;
  streamImg.src = streamUrl;
  streamUrlLabel.textContent = streamUrl;
  connectSocket(host);
};

const sendMove = () => {
  if (!socket || !socket.connected) {
    return;
  }
  socket.emit("move", {
    pan_speed: panSpeed,
    tilt_angle: tiltAngle,
  });
};

const setPanSpeed = (speed) => {
  panSpeed = clamp(speed, -PAN_SPEED_MAX, PAN_SPEED_MAX);
  updateTelemetry();
  sendMove();
};

const stopPan = () => {
  if (panSpeed === 0) {
    return;
  }
  setPanSpeed(0);
};

const setTiltAngle = (angle) => {
  tiltAngle = clamp(angle, TILT_MIN, TILT_MAX);
  updateTelemetry();
  sendMove();
};

const resizeOverlay = () => {
  if (!streamImg.naturalWidth || !streamImg.naturalHeight) {
    return;
  }
  overlay.width = streamImg.naturalWidth;
  overlay.height = streamImg.naturalHeight;
};

const clearOverlay = () => {
  overlayCtx.clearRect(0, 0, overlay.width, overlay.height);
};

const normalizeBox = (box, width, height) => {
  if (!box) {
    return null;
  }

  const rawWidth = box.width;
  const rawHeight = box.height;
  let rawXCenter = box.xCenter;
  let rawYCenter = box.yCenter;

  if (typeof rawXCenter !== "number" || typeof rawYCenter !== "number") {
    if (typeof box.xMin !== "number" || typeof box.yMin !== "number") {
      return null;
    }
    rawXCenter = box.xMin + rawWidth / 2;
    rawYCenter = box.yMin + rawHeight / 2;
  }

  if (
    typeof rawWidth !== "number" ||
    typeof rawHeight !== "number" ||
    typeof rawXCenter !== "number" ||
    typeof rawYCenter !== "number"
  ) {
    return null;
  }

  let xCenter = rawXCenter;
  let yCenter = rawYCenter;
  let boxWidth = rawWidth;
  let boxHeight = rawHeight;

  if (xCenter > 1 || yCenter > 1 || boxWidth > 1 || boxHeight > 1) {
    xCenter /= width;
    yCenter /= height;
    boxWidth /= width;
    boxHeight /= height;
  }

  return { xCenter, yCenter, width: boxWidth, height: boxHeight };
};

const pickLargestDetection = (detections, width, height) => {
  let bestBox = null;
  let bestArea = 0;

  detections.forEach((detection) => {
    const box = normalizeBox(detection.boundingBox, width, height);
    if (!box) {
      return;
    }
    const area = box.width * box.height;
    if (area > bestArea) {
      bestArea = area;
      bestBox = box;
    }
  });

  return bestBox;
};

const drawOverlay = (box) => {
  clearOverlay();
  if (!box) {
    return;
  }

  const x = (box.xCenter - box.width / 2) * overlay.width;
  const y = (box.yCenter - box.height / 2) * overlay.height;
  const w = box.width * overlay.width;
  const h = box.height * overlay.height;
  const centerX = box.xCenter * overlay.width;
  const centerY = box.yCenter * overlay.height;

  overlayCtx.strokeStyle = "rgba(45, 180, 162, 0.9)";
  overlayCtx.lineWidth = 3;
  overlayCtx.strokeRect(x, y, w, h);

  overlayCtx.fillStyle = "rgba(255, 107, 74, 0.9)";
  overlayCtx.beginPath();
  overlayCtx.arc(centerX, centerY, 5, 0, Math.PI * 2);
  overlayCtx.fill();

  overlayCtx.strokeStyle = "rgba(255, 255, 255, 0.6)";
  overlayCtx.lineWidth = 1;
  overlayCtx.beginPath();
  overlayCtx.moveTo(overlay.width / 2, 0);
  overlayCtx.lineTo(overlay.width / 2, overlay.height);
  overlayCtx.moveTo(0, overlay.height / 2);
  overlayCtx.lineTo(overlay.width, overlay.height / 2);
  overlayCtx.stroke();
};

const applyTracking = (xCenter, yCenter) => {
  const normX = (xCenter - 0.5) * 2;
  const normY = (yCenter - 0.5) * 2;

  const pan =
    Math.abs(normX) < PAN_DEADZONE
      ? 0
      : normX * PAN_SPEED_MAX * PAN_INVERT;
  setPanSpeed(pan);

  if (Math.abs(normY) < TILT_DEADZONE) {
    return;
  }

  const tiltDelta = clamp(
    normY * TILT_STEP_AUTO * TILT_INVERT,
    -TILT_MAX_STEP,
    TILT_MAX_STEP
  );
  setTiltAngle(tiltAngle + tiltDelta);
};

const handleDetections = (results) => {
  const width = streamImg.naturalWidth;
  const height = streamImg.naturalHeight;
  if (!width || !height) {
    return;
  }

  const detections = results.detections || [];
  if (!detections.length) {
    drawOverlay(null);
    setVisionStatus("No face", "warn");
    if (trackingEnabled) {
      stopPan();
    }
    return;
  }

  const bestBox = pickLargestDetection(detections, width, height);
  if (!bestBox) {
    drawOverlay(null);
    setVisionStatus("No face", "warn");
    if (trackingEnabled) {
      stopPan();
    }
    return;
  }

  drawOverlay(bestBox);
  setVisionStatus("Face detected", "ok");

  if (trackingEnabled) {
    applyTracking(bestBox.xCenter, bestBox.yCenter);
  }
};

const detectLoop = async () => {
  if (!detectionReady) {
    return;
  }

  const now = performance.now();
  if (detectionBusy || now - lastDetectAt < DETECT_INTERVAL) {
    requestAnimationFrame(detectLoop);
    return;
  }

  if (!streamImg.naturalWidth || !streamImg.naturalHeight) {
    requestAnimationFrame(detectLoop);
    return;
  }

  detectionBusy = true;
  lastDetectAt = now;

  try {
    await faceDetection.send({ image: streamImg });
  } catch (error) {
    setVisionStatus("Vision blocked (CORS)", "warn");
    detectionReady = false;
    stopPan();
  } finally {
    detectionBusy = false;
  }

  requestAnimationFrame(detectLoop);
};

const initFaceDetection = () => {
  if (typeof FaceDetection === "undefined") {
    setVisionStatus("Vision missing", "warn");
    return;
  }

  faceDetection = new FaceDetection({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`,
  });
  faceDetection.setOptions({
    model: "short",
    minDetectionConfidence: DETECT_MIN_SCORE,
  });
  faceDetection.onResults(handleDetections);
  detectionReady = true;
  setVisionStatus("Vision ready", "warn");
  requestAnimationFrame(detectLoop);
};

const handleManualTilt = (delta) => {
  if (trackingEnabled) {
    return;
  }
  setTiltAngle(tiltAngle + delta);
};

const handleManualPan = (speed) => {
  if (trackingEnabled) {
    return;
  }
  setPanSpeed(speed);
};

trackingToggle.addEventListener("click", () => {
  setTrackingEnabled(!trackingEnabled);
});

downBtn.addEventListener("click", () => handleManualTilt(TILT_STEP));
upBtn.addEventListener("click", () => handleManualTilt(-TILT_STEP));

leftBtn.addEventListener("pointerdown", () =>
  handleManualPan(-PAN_SPEED_MANUAL)
);
rightBtn.addEventListener("pointerdown", () =>
  handleManualPan(PAN_SPEED_MANUAL)
);

["pointerup", "pointerleave", "pointercancel"].forEach((evt) => {
  leftBtn.addEventListener(evt, stopPan);
  rightBtn.addEventListener(evt, stopPan);
});

window.addEventListener("blur", stopPan);
document.addEventListener("visibilitychange", () => {
  if (document.hidden) {
    stopPan();
  }
});

streamImg.addEventListener("load", resizeOverlay);

updateTelemetry();
setTrackingEnabled(false);
connectToDevice();
initFaceDetection();
