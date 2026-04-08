from flask import Flask, request, jsonify
import time

app = Flask(__name__)


@app.route('/api/move', methods=['POST'])
def move():
    data = request.json
    pan_adj = data.get('pan', 0)
    tilt_adj = data.get('tilt', 0)
    
    
    print(f"[RUCH] Obracam kamerę: Pan(X): {pan_adj}°, Tilt(Y): {tilt_adj}°")
    
    return jsonify({"status": "success", "pan": pan_adj, "tilt": tilt_adj})

if __name__ == '__main__':
    print("Serwer silników nasłuchuje na porcie 5001...")
    app.run(host='0.0.0.0', port=5001)