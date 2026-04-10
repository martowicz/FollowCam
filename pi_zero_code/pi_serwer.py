import socketio
import eventlet
import pigpio
import sys

PAN_PIN = 18
TILT_PIN = 12

PAN_STOP = 1500

pi= pigpio.pi()

if not pi.connected:
    print("BŁĄD: Nie można połączyć się z demonem pigpiod!")
    print("Upewnij się, że wpisałeś: sudo systemctl start pigpiod")
    sys.exit()


def set_pan_speed(speed):
    if speed == 0: pi.set_servo_pulsewidth(PAN_PIN, PAN_STOP)

    else:
        speed = max(-100, min(100, speed))
        pulsewidth = PAN_STOP + (speed*5)
        pi.set_servo_pulsewidth(PAN_PIN, pulsewidth)

def set_tilt_angle(angle):
    angle = max(0, min(180, angle))
    pulsewidth = 500 + (angle * 2000 / 180)
    pi.set_servo_pulsewidth(TILT_PIN, pulsewidth)





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
        
        set_pan_speed(pan_speed)
        set_tilt_angle(tilt_angle)
        
    except Exception as e:
        print(f"Błąd sterowania: {e}")
    

@sio.event
def disconnect(sid):
    print(f"Rozłączono: {sid}")

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
        # Odcięcie zasilania sygnałowego serw przy wyłączeniu skryptu
        pi.set_servo_pulsewidth(PAN_PIN, 0)
        pi.set_servo_pulsewidth(TILT_PIN, 0)
        pi.stop()