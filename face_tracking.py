import cv2
import threading
import time
from typing import Generator
from picamera2 import Picamera2

class FaceTracker:
    def __init__(
        self, 
        camera_index=0, 
        camera_backend="auto", 
        frame_width=320, 
        frame_height=240,
        source_fps=10,             # <-- O to pytał main.py!
        scale_factor=1.5, 
        min_neighbors=6, 
        detection_scale=0.25,      # <-- O to pytał main.py!
        frame_skip=12,             # <-- O to pytał main.py!
        jpeg_quality=35            # <-- O to pytał main.py!
    ):
        # 1. Przypisanie argumentów do zmiennych klasy
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.detection_scale = detection_scale
        self.frame_skip = frame_skip
        self.jpeg_quality = jpeg_quality
        self.source_fps = source_fps
        
        # 2. Inicjalizacja detekcji twarzy
        self.face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        if self.face_cascade.empty():
            raise RuntimeError("Brak pliku haarcascade_frontalface_default.xml")

        # 3. Inicjalizacja Picamera2
        print("--- Inicjalizacja Picamera2 ---")
        self.picam2 = Picamera2()
        config = self.picam2.create_video_configuration(main={"size": (frame_width, frame_height), "format": "RGB888"})
        self.picam2.configure(config)
        self.picam2.start()
        print("--- Kamera gotowa ---")
        
        # 4. Zmienne dla wielowątkowości
        self.frame = None
        self.last_faces = []
        self.stopped = False
        self.lock = threading.Lock()

        # Uruchomienie wątku tła
        threading.Thread(target=self._update_thread, daemon=True).start()

    def _update_thread(self):
        frame_count = 0
        inv_scale = 1.0 / self.detection_scale
        
        # Przeliczamy FPS na czas uśpienia (żeby procesor mógł odpocząć)
        sleep_time = 1.0 / self.source_fps if self.source_fps > 0 else 0.1

        while not self.stopped:
            try:
                # Pobieranie klatki z Picamera2
                frame_rgb = self.picam2.capture_array()
                frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"Błąd czytania klatki: {e}")
                time.sleep(0.1)
                continue

            frame_count += 1

            # Detekcja tylko co N-tą klatkę
            if frame_count % self.frame_skip == 0:
                small = cv2.resize(frame, (0, 0), fx=self.detection_scale, fy=self.detection_scale)
                gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
                
                faces = self.face_cascade.detectMultiScale(
                    gray, scaleFactor=self.scale_factor, minNeighbors=self.min_neighbors, minSize=(30, 30)
                )

                temp_faces = []
                for (x, y, w, h) in faces:
                    temp_faces.append((int(x * inv_scale), int(y * inv_scale), int(w * inv_scale), int(h * inv_scale)))
                
                with self.lock:
                    self.last_faces = temp_faces

            # Rysowanie ramek
            with self.lock:
                for (x, y, w, h) in self.last_faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                cv2.putText(frame, f"Faces: {len(self.last_faces)}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                self.frame = frame.copy()
            
            # Wymuszony odpoczynek procesora na podstawie source_fps z main.py
            time.sleep(sleep_time)

    def frames(self) -> Generator[bytes, None, None]:
        while not self.stopped:
            if self.frame is not None:
                with self.lock:
                    # Używamy jakości JPEG podanej w main.py
                    ok, buffer = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, self.jpeg_quality])
                if ok:
                    yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.05)

    def release(self) -> None:
        self.stopped = True
        self.picam2.stop()