import socketio
import time

# PAMIĘTAJ: To musi być IP Twojej Malinki i port 5000!
PI_IP = "http://192.168.0.43:5000"

sio = socketio.Client()

@sio.event
def connect():
    print("✅ Połączono z serwerem Malinki!")

@sio.event
def disconnect():
    print("❌ Rozłączono.")

def run_tests():
    print(f"Łączenie z {PI_IP}...")
    try:
        sio.connect(PI_IP)
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        print("Upewnij się, że serwer na Malince jest uruchomiony!")
        return
    
    print("\n--- TEST 1: Oś TILT (Kąty) ---")
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 150})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 160})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 170})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 180})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 190})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 200})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 210})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 220})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 230})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 240})
    time.sleep(1)
    sio.emit('move', {'pan_speed': 0, 'tilt_angle': 250})
    time.sleep(1)
    
    
    # print("\n--- TEST 2: Oś PAN (Prędkość) ---")
    # print("Kamera obraca się w lewo (prędkość -40)...")
    # sio.emit('move', {'pan_speed': -40, 'tilt_angle': 90})
    # time.sleep(1.5)
    # sio.emit('move', {'pan_speed': 40, 'tilt_angle': 90})
    # time.sleep(1.5)
    # sio.emit('move', {'pan_speed': 80, 'tilt_angle': 90})
    # time.sleep(1.5)
    
    print("\nTesty zakończone. Zamykam połączenie.")
    sio.disconnect()

if __name__ == '__main__':
    run_tests()