import socketio

# Tworzymy klienta
sio = socketio.Client()

def connect_to_pi(ip):
    try:
        sio.connect(f'http://{ip}:5000')
        print("Połączono z serwerem WebSocket na Pi!")
    except Exception as e:
        print(f"Błąd połączenia: {e}")

def send_move_command(pan, tilt):
    if sio.connected:
        # Emitujemy zdarzenie zamiast robić POST
        sio.emit('move', {'pan': pan, 'tilt': tilt})
    else:
        print("Brak połączenia! Nie można wysłać ruchu.")

# Funkcja do czystego rozłączenia przy wyjściu z programu
def disconnect_pi():
    if sio.connected:
        sio.disconnect()