import socket
import json
import random

SERVER = '127.0.0.1'
PORT = 5000

def send_task(payload):
    """Envía una tarea al servidor y espera el resultado."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER, PORT))
        task = {
            "id": random.randint(1000, 9999),
            "payload": payload
        }
        s.sendall(json.dumps(task).encode('utf-8'))
        data = s.recv(4096)
        result = json.loads(data.decode('utf-8'))
        print(f"[Client] Resultado recibido: {result}")

if __name__ == "__main__":
    for n in range(5):
        send_task(f"Tarea-{n}")
