import socket
import threading
import queue
import json
import time
import random
import sys

# Simulación de RabbitMQ interna (cola de tareas)
task_queue = queue.Queue()
result_queue = queue.Queue()

HOST = '0.0.0.0'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
MAX_WORKERS = 4

def worker_thread(worker_id):
    """Simula un worker que procesa tareas."""
    while True:
        task = task_queue.get()
        if task is None:
            break
        print(f"[Worker-{worker_id}] Procesando tarea: {task}")
        time.sleep(random.uniform(1, 3))  # simula carga
        result = {
            "worker": worker_id,
            "input": task,
            "output": f"Resultado procesado de {task['payload']}"
        }
        result_queue.put(result)
        task_queue.task_done()

def handle_client(conn, addr):
    """Recibe tareas de un cliente, las agrega a la cola y devuelve resultados."""
    with conn:
        print(f"[Server] Conectado con {addr}")
        data = conn.recv(4096)
        if not data:
            return
        task = json.loads(data.decode('utf-8'))
        task_queue.put(task)

        # Espera un resultado correspondiente
        result = result_queue.get()
        conn.sendall(json.dumps(result).encode('utf-8'))
        print(f"[Server] Resultado enviado a {addr}")

def main():
    print("[Server] Iniciando servidor distribuido...")
    
    # Lanzamos el pool de threads
    for i in range(MAX_WORKERS):
        threading.Thread(target=worker_thread, args=(i,), daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Server] Escuchando en {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
