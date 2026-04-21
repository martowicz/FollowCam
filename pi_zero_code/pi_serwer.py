import socketio
import hardware
from werkzeug.serving import run_simple

# async_mode='threading' to klucz! 
# Pozwala bibliotece sprzętowej robić swoje, nie blokując sieci.
sio = socketio.Server(cors_allowed_origins='*', async_mode='threading')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"✅ Połączono z mózgiem! ID sesji: {sid}")

@sio.on('move')
def handle_move(sid, data):
    try:
        pan_speed = data.get('pan_speed', 0)
        tilt_angle = data.get('tilt_angle', 90)
        
        hardware.set_pan_speed(pan_speed)
        hardware.set_tilt_angle(tilt_angle)
        
    except Exception as e:
        print(f"⚠️ Błąd sterowania (move): {e}")

@sio.event
def disconnect(sid):
    print(f"❌ Rozłączono: {sid}. Próbuję zatrzymać silniki...")
    try:
        hardware.set_pan_speed(0)
    except Exception as e:
        print(f"⚠️ Błąd przy zatrzymywaniu silnika: {e}")

if __name__ == '__main__':
    print("------------------------------------------")
    print("SERWER FOLLOW-CAM (TRYB STABILNY) GOTOWY")
    print(f"Nasłuchiwanie na porcie: 5000")
    print("------------------------------------------")
    
    try:
        # Używamy standardowego serwera, threaded=True zapobiega zawieszaniu
        run_simple('0.0.0.0', 5000, app, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\nZamykanie serwera...")
    finally:
        try:
            hardware.cleanup()
        except Exception as e:
            print(f"Błąd podczas czyszczenia pinów: {e}")