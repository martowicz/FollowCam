import cv2

class FaceDetector:
    def __init__(self):
        # OpenCV ma to wbudowane! Nie musisz pobierać żadnych plików .tflite.
        # cv2.data.haarcascades to ścieżka do gotowych modeli dostarczanych z biblioteką.
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def find_face_center(self, frame):
        # Kaskady Haara działają najlepiej i najszybciej na obrazie czarno-białym
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Wykrywamy twarze na klatce
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50) # Minimalny rozmiar twarzy, żeby ignorować fałszywe detekcje
        )

        # Jeśli wykryto przynajmniej jedną twarz
        if len(faces) > 0:
            # Bierzemy tylko pierwszą z brzegu twarz (indeks 0)
            (x, y, w, h) = faces[0]
            
            # Wyliczamy jej środek
            cx = x + w // 2
            cy = y + h // 2
            
            # Rysujemy kwadrat i czerwoną kropkę na środku
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            
            return cx, cy, frame
            
        return None, None, frame