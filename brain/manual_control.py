import cv2
import time
from vision import FaceDetector
import pi_client

# PAMIĘTAJ: Podmień na prawdziwe IP Twojej Malinki!
STREAM_URL = "http://192.168.0.43:8080/stream"

def main():
    print("Łączenie z kamerą Raspberry Pi...")
    cap = cv2.VideoCapture(STREAM_URL)
    detector = FaceDetector()
    
    # Parametry ręcznego sterowania
    current_tilt = 90
    pan_speed = 0
    TILT_STEP = 5         # O ile stopni rusza się kamera przy jednym wciśnięciu W/S
    PAN_SPEED_MANUAL = 30 # Prędkość obrotu przy wciśnięciu A/D
    
    window_name = "Mozg FollowCam - TRYB RECZNY"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    pi_client.connect_to_pi("192.168.0.43") # IP Malinki
    
    print("\n--- STEROWANIE RĘCZNE ---")
    print("[A] / [D] - Kręć w lewo/prawo (PAN)")
    print("[SPACJA]  - ZATRZYMAJ obrót (Hamulec!)")
    print("[W] / [S] - Kamera góra/dół (TILT)")
    print("[Q]       - Wyjście z programu\n")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Zgubiono klatkę. Czekam...")
            time.sleep(0.5)
            continue
            
        # Nadal przetwarzamy obraz i szukamy twarzy dla samego podglądu, 
        # ale IGNORUJEMY współrzędne (cx, cy) do sterowania.
        cx, cy, processed_frame = detector.find_face_center(frame)
        
        # --- NASŁUCHIWANIE KLAWIATURY ---
        # Czas oczekiwania 10ms zapewnia płynny obraz i szybką reakcję
        key = cv2.waitKey(10) & 0xFF
        
        if key == ord('q'):
            print("Zamykanie programu...")
            pi_client.send_move_command(0, 90) # Bezpieczny powrót na środek
            break
            
        # --- LOGIKA STEROWANIA RĘCZNEGO ---
        elif key == ord('a'):
            pan_speed = -PAN_SPEED_MANUAL
        elif key == ord('d'):
            pan_speed = PAN_SPEED_MANUAL
        elif key == ord(' '):
            pan_speed = 0  # Spacja to hamulec osi PAN
            
        elif key == ord('w'):
            current_tilt -= TILT_STEP
        elif key == ord('s'):
            current_tilt += TILT_STEP
            
        # Zabezpieczenie przed mechanicznym uszkodzeniem serwa TILT (tylko 0-180)
        current_tilt = max(0, min(180, current_tilt))
        
        # WYSYŁANIE KOMEND DO MALINKI (co każdą klatkę)
        pi_client.send_move_command(pan_speed, current_tilt)
        print("wysłano komende: ", pan_speed, " ", current_tilt)

        # Rysowanie parametrów na ekranie dla łatwiejszego debugowania
        cv2.putText(processed_frame, f"TILT (Kat): {current_tilt}st (W/S)", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(processed_frame, f"PAN (Predkosc): {pan_speed} (A/D/Spacja)", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        # Wyświetlamy okno
        cv2.imshow(window_name, processed_frame)
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()