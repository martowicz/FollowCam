import socketio
import keyboard
import time

# ==========================================
# KONFIGURACJA
# ==========================================
PI_IP = "http://192.168.0.43:5000"
PAN_SPEED_VAL = 30
TILT_STEP = 10

current_tilt = 185
last_pan = 0

sio = socketio.Client(logger=False, engineio_logger=False)

@sio.event
def connect():
    print("\n✅ POŁĄCZONO! Serwer gotowy na komendy.")

@sio.event
def disconnect():
    print("\n❌ ROZŁĄCZONO.")

if __name__ == '__main__':
    print(f"Łączenie z {PI_IP}...")
    try:
        sio.connect(PI_IP)
    except Exception as e:
        print(f"⚠️ Błąd: {e}")
        exit()
        
    print("=========================================")
    print("🎮 TRYB STEROWANIA RĘCZNEGO AKTYWNY")
    print("=========================================")
    print("[W] / [S] - Kamera góra/dół")
    print("[A] / [D] - Kamera lewo/prawo (trzymaj)")
    print("[Q] - Zakończ program")
    print("=========================================")

    try:
        while True:
            # Wychodzenie z pętli
            if keyboard.is_pressed('q'):
                break

            # Obsługa TILT (skokowo z opóźnieniem, żeby serwo nie odleciało za daleko)
            if keyboard.is_pressed('w'):
                current_tilt = max(90, current_tilt - TILT_STEP) # Zmień 90 na swój limit
                sio.emit('move', {'pan_speed': last_pan, 'tilt_angle': current_tilt})
                print(f"📡 TILT W GÓRĘ -> Kąt: {current_tilt}")
                time.sleep(0.15)
            elif keyboard.is_pressed('s'):
                current_tilt = min(270, current_tilt + TILT_STEP) # Zmień 270 na swój limit
                sio.emit('move', {'pan_speed': last_pan, 'tilt_angle': current_tilt})
                print(f"📡 TILT W DÓŁ -> Kąt: {current_tilt}")
                time.sleep(0.15)

            # Obsługa PAN (płynnie)
            if keyboard.is_pressed('a'):
                current_pan = -PAN_SPEED_VAL
            elif keyboard.is_pressed('d'):
                current_pan = PAN_SPEED_VAL
            else:
                current_pan = 0

            # Wysyłamy komendę PAN tylko wtedy, gdy wcisnąłeś lub puściłeś klawisz
            if current_pan != last_pan:
                sio.emit('move', {'pan_speed': current_pan, 'tilt_angle': current_tilt})
                if current_pan == 0:
                    print("🛑 STOP PAN")
                else:
                    print(f"📡 OBRÓT PAN -> Prędkość: {current_pan}")
                last_pan = current_pan

            # Krótka pauza, żeby nie zamęczyć procesora w laptopie
            time.sleep(0.05)
            
    except Exception as e:
        print(f"⚠️ Błąd klawiatury: {e}")

    print("\nZamykanie...")
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': current_tilt})
    time.sleep(0.5)
    sio.disconnect()