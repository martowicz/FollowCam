import socketio
import eventlet
import hardware


sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"Połączono z mózgiem! ID sesji: {sid}")

@sio.on('move')
def handle_move(sid, data):
    try:
        pan_speed = data.get('pan_speed', 0)
        tilt_angle = data.get('tilt_angle', 90)
        
        hardware.set_pan_speed(pan_speed)
        hardware.set_tilt_angle(tilt_angle)
        
    except Exception as e:
        print(f"Błąd sterowania: {e}")
    

@sio.event
def disconnect(sid):
    print(f"Rozłączono: {sid}")
    hardware.set_pan_speed(0)


if __name__ == '__main__':
    print("------------------------------------------")
    print("SERWER FOLLOW-CAM (HARDWARE PWM) GOTOWY")
    print(f"Nasłuchiwanie na porcie: 5000")
    print("------------------------------------------")
    
    try:
        eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
    finally:
        hardware.cleanup()