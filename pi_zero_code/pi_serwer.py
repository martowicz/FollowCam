import socketio
import eventlet


sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print(f"Połączono z mózgiem! ID sesji: {sid}")

@sio.on('move')
def handle_move(sid, data):
    pan = data.get('pan', 0)
    tilt = data.get('tilt', 0)
    
    print(f"[RUCH WS] Pan: {pan}°, Tilt: {tilt}°")
    

@sio.event
def disconnect(sid):
    print(f"Rozłączono: {sid}")

if __name__ == '__main__':
    print("Serwer WebSocket startuje na porcie 5000...")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)