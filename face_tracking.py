import importlib
from pathlib import Path
from typing import Generator

import cv2


def _is_raspberry_pi() -> bool:
    model_path = Path("/proc/device-tree/model")
    if not model_path.exists():
        return False

    try:
        model_text = model_path.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False

    return "raspberry pi" in model_text


class OpenCVCamera:
    def __init__(self, camera_index: int) -> None:
        self.capture = cv2.VideoCapture(camera_index)
        if not self.capture.isOpened():
            raise RuntimeError(
                "Could not open camera via OpenCV. On macOS, grant camera permissions to your terminal/IDE."
            )

    def read(self) -> tuple[bool, object]:
        return self.capture.read()

    def release(self) -> None:
        self.capture.release()


class PiCamera2Camera:
    def __init__(self, frame_width: int, frame_height: int) -> None:
        try:
            picamera2_module = importlib.import_module("picamera2")
            picamera2_class = getattr(picamera2_module, "Picamera2")
        except ImportError as exc:
            raise RuntimeError(
                "Picamera2 backend requires picamera2. Install on Raspberry Pi: sudo apt install -y python3-picamera2"
            ) from exc

        self.camera = picamera2_class()
        config = self.camera.create_video_configuration(
            main={"size": (frame_width, frame_height), "format": "RGB888"}
        )
        self.camera.configure(config)
        self.camera.start()

    def read(self) -> tuple[bool, object]:
        frame_rgb = self.camera.capture_array()
        if frame_rgb is None:
            return False, None

        if len(frame_rgb.shape) == 3 and frame_rgb.shape[2] == 4:
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGBA2BGR)
        else:
            frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        return True, frame_bgr

    def release(self) -> None:
        try:
            self.camera.stop()
        finally:
            close_method = getattr(self.camera, "close", None)
            if callable(close_method):
                close_method()


class FaceTracker:
    def __init__(
        self,
        camera_index: int,
        scale_factor: float,
        min_neighbors: int,
        camera_backend: str = "auto",
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> None:
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.active_backend = "opencv"

        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            raise RuntimeError(f"Could not load Haar cascade from: {cascade_path}")

        self.camera = self._create_camera(
            camera_index=camera_index,
            camera_backend=camera_backend,
            frame_width=frame_width,
            frame_height=frame_height,
        )

    def _create_camera(
        self,
        camera_index: int,
        camera_backend: str,
        frame_width: int,
        frame_height: int,
    ) -> object:
        if camera_backend == "opencv":
            self.active_backend = "opencv"
            return OpenCVCamera(camera_index)

        if camera_backend == "picamera2":
            self.active_backend = "picamera2"
            return PiCamera2Camera(frame_width, frame_height)

        if camera_backend == "auto":
            if _is_raspberry_pi():
                try:
                    camera = PiCamera2Camera(frame_width, frame_height)
                    self.active_backend = "picamera2"
                    print("Using camera backend: picamera2")
                    return camera
                except Exception as exc:
                    print(f"Picamera2 backend unavailable ({exc}). Falling back to OpenCV.")

            self.active_backend = "opencv"
            print("Using camera backend: opencv")
            return OpenCVCamera(camera_index)

        raise ValueError(
            "Invalid camera backend. Use one of: auto, opencv, picamera2."
        )

    def frames(self) -> Generator[bytes, None, None]:
        while True:
            ok, frame = self.camera.read()
            if not ok or frame is None:
                continue

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray_frame,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=(60, 60),
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                center_x = x + w // 2
                center_y = y + h // 2
                cv2.circle(frame, (center_x, center_y), 4, (0, 255, 0), -1)

                text_y = y - 10 if y > 20 else y + h + 20
                cv2.putText(
                    frame,
                    f"Center: ({center_x}, {center_y})",
                    (x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            cv2.putText(
                frame,
                f"Faces: {len(faces)}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

            ok_encode, buffer = cv2.imencode(".jpg", frame)
            if not ok_encode:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

    def release(self) -> None:
        self.camera.release()
