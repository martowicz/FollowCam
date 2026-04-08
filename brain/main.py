import cv2
import time
from vision import FaceDetector
from pi_client import send_move_command

# PAMIĘTAJ: Podmień na prawdziwe IP Twojej Malinki!
STREAM_URL = "http://192.168.0.43:8080/stream"

def main():
    print("Łączenie z kamerą Raspberry Pi...")
    cap = cv2.VideoCapture(STREAM_URL)
    detector = FaceDetector()
    
    # Środek ekranu dla rozdzielczości 640x480
    TARGET_X = 320 
    TARGET_Y = 240
    
    # ==========================================
    # FIX NA LINUXA: TWORZYMY OKNO TYLKO RAZ
    # ==========================================
    # Używamy nazwy bez polskich znaków, żeby Linux się nie pogubił
    window_name = "Mozg FollowCam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Zgubiono klatkę. Czekam...")
            time.sleep(0.5)
            continue
            
        # Szukamy twarzy za pomocą kaskad Haara (z pliku vision.py)
        cx, cy, processed_frame = detector.find_face_center(frame)
        
        if cx is not None and cy is not None:
            # Obliczamy błąd (odległość twarzy od środka)
            error_x = TARGET_X - cx
            error_y = TARGET_Y - cy
            
            # Wyliczamy korektę dla silników
            pan_adj = round(error_x * 0.05)
            tilt_adj = round(error_y * 0.05)
            
            # Wysyłamy komendę do Malinki (na razie będzie to tylko log w terminalu Pi Zero)
            if abs(pan_adj) > 1 or abs(tilt_adj) > 1:
                send_move_command(pan_adj, tilt_adj)

        # Wyświetlamy płynny obraz w tym JEDNYM, konkretnym oknie
        cv2.imshow(window_name, processed_frame)
        
        # To jest krytyczne dla Linuxa - pozwala mu odświeżyć grafikę w oknie!
        # Wyjście pod klawiszem 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Zamykanie programu...")
            break
            
    # Eleganckie sprzątanie po zamknięciu
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()