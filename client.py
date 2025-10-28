import socket
import json
import random
import sys
from datetime import datetime

SERVER = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 5000


def send_task(payload):
    """Envía una tarea JSON al servidor distribuido y recibe el resultado procesado."""
    task = {
        "id": random.randint(1000, 9999),
        "payload": payload
    }

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [Client] Conectando a {SERVER}:{PORT}...")
            s.connect((SERVER, PORT))
            s.sendall(json.dumps(task).encode('utf-8'))
            print(f"[Client] Tarea enviada: {task}")

            data = s.recv(4096)
            if not data:
                print("[Client] ⚠️ Sin respuesta del servidor.")
                return

            result = json.loads(data.decode('utf-8'))
            print(f"[Client] ✅ Resultado recibido: {result}\n")

    except ConnectionRefusedError:
        print(f"[Error] No se pudo conectar al servidor {SERVER}:{PORT}. ¿Está en ejecución?")
    except json.JSONDecodeError:
        print("[Error] Respuesta inválida (JSON corrupto).")
    except Exception as e:
        print(f"[Error inesperado] {e}")

if __name__ == "__main__":
    print("[Client] Iniciando envío de tareas...\n")
    for n in range(5):
        send_task(f"Tarea-{n}")
