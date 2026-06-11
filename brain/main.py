import cv2
import time
from vision import FaceDetector
import pi_client

# PAMIĘTAJ: Podmień na prawdziwe IP Twojej Malinki!
pi_ip_address = "192.168.2.43"
STREAM_URL = "http://" + pi_ip_address + ":8080/stream"

def main():
    print("Łączenie z kamerą Raspberry Pi...")
    cap = cv2.VideoCapture(STREAM_URL)
    detector = FaceDetector()
    
    # Rozdzielczość strumienia
    TARGET_X = 320 
    TARGET_Y = 240
    
    # MARTWA STREFA (Deadzone) - margines błędu w pikselach. 
    # Jeśli twarz jest w tym promieniu od środka, kamera się nie rusza.
    DEADZONE_X = 40
    DEADZONE_Y = 30
    
    # Pamięć dla serwa TILT (180 stopni). Startujemy od środka.
    current_tilt = 90
    
    window_name = "Mozg FollowCam"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    pi_client.connect_to_pi(pi_ip_address)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Zgubiono klatkę. Czekam...")
            time.sleep(0.5)
            continue
            
        cx, cy, processed_frame = detector.find_face_center(frame)
        
        if cx is not None and cy is not None:
            # Obliczamy błąd - konwencja:
            # error_x > 0 oznacza twarz po prawej stronie
            # error_y > 0 oznacza twarz w dolnej części ekranu
            error_x = cx - TARGET_X
            error_y = cy - TARGET_Y
            
            # --- 1. OŚ TILT (KĄTY DLA SERWA 180) ---
            if abs(error_y) > DEADZONE_Y:
                # Jeśli twarz ucieka, powoli dodajemy lub odejmujemy stopnie
                tilt_step = round(error_y * 0.03) # 0.03 to "czułość"
                current_tilt += tilt_step
                # Zabezpieczenie przed przekręceniem poniżej 0 i powyżej 180
                current_tilt = max(0, min(180, current_tilt))
                
            # --- 2. OŚ PAN (PRĘDKOŚĆ DLA SERWA 360) ---
            pan_speed = 0
            if abs(error_x) > DEADZONE_X:
                # Prędkość proporcjonalna do błędu (im dalej twarz, tym szybciej goni)
                pan_speed = round(error_x * 0.15) # 0.15 to "czułość pedału gazu"
                # Zabezpieczenie prędkości maksymalnej do zakresu -100 ... 100
                pan_speed = max(-100, min(100, pan_speed))
            
            # Wysyłamy aktualne wartości do Malinki
            pi_client.send_move_command(pan_speed, current_tilt)
            
        else:
            # CRITICAL: Twarz zniknęła! 
            # Musimy krzyczeć "STOP" dla serwa 360, inaczej będzie się kręcić w nieskończoność
            pi_client.send_move_command(0, current_tilt)

        # Rysowanie na ekranie (dla debugowania)
        cv2.putText(processed_frame, f"TILT (Kat): {current_tilt}st", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        if cx is not None:
            cv2.putText(processed_frame, f"PAN (Predkosc): {pan_speed}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        cv2.imshow(window_name, processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Zamykanie programu...")
            # Zatrzymanie ruchu przed wyjściem
            pi_client.send_move_command(0, 90)
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()