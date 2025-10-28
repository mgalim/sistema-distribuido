import socket
import threading
import queue
import json
import time
import random
import sys
import sqlite3
from datetime import datetime

task_queue = queue.Queue()
result_queue = queue.Queue()

HOST = '127.0.0.1' 
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
MAX_WORKERS = 4
DB_NAME = "resultados.db"


def init_db():
    """Crea la base de datos y la tabla de resultados si no existen."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            worker_id TEXT,
            input TEXT,
            output TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def guardar_resultado(result):
    """Guarda el resultado procesado en la base SQLite local."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        INSERT INTO resultados (worker_id, input, output)
        VALUES (?, ?, ?)
    """, (str(result["worker"]), json.dumps(result["input"]), result["output"]))
    conn.commit()
    conn.close()


def ip_permitida(ip):
    """Verifica si la IP pertenece a una red privada o localhost."""
    return (
        ip.startswith("127.") or
        ip.startswith("192.168.") or
        ip.startswith("10.") or
        ip.startswith("172.")
    )


def worker_thread(worker_id):
    """Simula un worker que procesa tareas."""
    while True:
        task = task_queue.get()
        if task is None:
            break
        print(f"[Worker-{worker_id}] Procesando tarea: {task}")
        time.sleep(random.uniform(1, 3))  # Simula carga

        result = {
            "worker": worker_id,
            "input": task,
            "output": f"Resultado procesado de {task['payload']}",
            "timestamp": datetime.now().isoformat()
        }

        guardar_resultado(result)
        result_queue.put(result)
        task_queue.task_done()


def handle_client(conn, addr):
    """Recibe tareas de un cliente, las encola y devuelve resultados procesados."""
    print(f"[Server] Conexión entrante desde {addr}")

    if not ip_permitida(addr[0]):
        print(f"[Security] Conexión rechazada desde {addr[0]} (IP no permitida).")
        conn.close()
        return

    with conn:
        try:
            data = conn.recv(4096)
            if not data:
                return

            task = json.loads(data.decode('utf-8'))
            print(f"[Server] Tarea recibida: {task}")
            task_queue.put(task)

            result = result_queue.get()
            conn.sendall(json.dumps(result).encode('utf-8'))
            print(f"[Server] Resultado enviado a {addr}")

        except Exception as e:
            print(f"[Error] {e}")


def main():
    print("[Server] Iniciando servidor distribuido...")

    init_db()

    # Lanzamos el pool de threads
    for i in range(MAX_WORKERS):
        threading.Thread(target=worker_thread, args=(i,), daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Evita error de puerto ocupado
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Server] Escuchando en {HOST}:{PORT}")

        try:
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\n[Server] Apagando servidor...")

if __name__ == "__main__":
    main()
