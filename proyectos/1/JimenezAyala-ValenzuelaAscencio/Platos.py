from Champion import *

# Platos.py
import threading

class Platos:
    # Constructor
    def __init__(self, k):
        self.semaforo = threading.Semaphore(k) # Semáforo para los platos
        self.lock = threading.Lock() # Lock de semáforo para inhabilitar el acceso
        self.platos_disponibles = k # Cantidad de platos

    def tomar(self, cliente_id):
        # Bloqueamos y revisamos si hay platos disponibles
        with self.lock:
            if self.platos_disponibles == 0:
                print(f"[Cliente {cliente_id}] QUIERE UN PLATO, pero no hay disponibles. Esperando...")
        self.semaforo.acquire() # Accedemos al plato
        # Bloqueamos para tomarlo
        with self.lock:
            self.platos_disponibles -= 1 # Disminuimos el contador
            print(f"[Cliente {cliente_id}] Tomó un plato. Quedan {self.platos_disponibles} disponibles.")

    # Devolvemos el plato
    def devolver(self):
        with self.lock:
            self.platos_disponibles += 1 # Aumentamos el contador
            print(f"Un plato fue devuelto. Hay ahora {self.platos_disponibles} disponibles.")
        self.semaforo.release() # Liberamos el semáforo
