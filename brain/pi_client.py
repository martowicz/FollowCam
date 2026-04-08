import requests

# Podmień na prawdziwe IP Twojej Malinki!
PI_URL = "http://192.168.0.43:5001/api/move"

def send_move_command(pan, tilt):
    try:
        payload = {"pan": pan, "tilt": tilt}
        # Wysyłamy komendę z krótkim limitem czasu, żeby nie zawiesić laptopa
        response = requests.post(PI_URL, json=payload, timeout=0.1)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        print("[BŁĄD] Nie można połączyć się z serwerem silników na Pi Zero!")
        return False