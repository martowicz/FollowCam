import socketio

# Tworzymy klienta
sio = socketio.Client()

def connect_to_pi(ip):
    try:
        sio.connect(f'http://{ip}:5000')
        print("Połączono z serwerem WebSocket na Pi!")
    except Exception as e:
        print(f"Błąd połączenia: {e}")

def send_move_command(pan_speed, tilt_angle):
    # Malinka oczekuje kluczy 'pan_speed' i 'tilt_angle'
    if sio.connected:
        sio.emit('move', {'pan_speed': pan_speed, 'tilt_angle': tilt_angle})

# Funkcja do czystego rozłączenia przy wyjściu z programu
def disconnect_pi():
    if sio.connected:
        sio.disconnect()