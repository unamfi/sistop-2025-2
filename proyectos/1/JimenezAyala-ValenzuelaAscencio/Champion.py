import threading
import time
import random

class Champion:
    # Constructor únicamente con dos locks para realizar Mutex
    def __init__(self):
        self.lock_servir = threading.Lock()  # Lock para servir
        self.lock_cobrar = threading.Lock()  # Lock para cobrar
        self.estado = "Inactivo"  # Estado inicial

    # Función para servir tacos
    def servir_tacos(self, cliente_id):
        with self.lock_servir:  # Bloqueamos para servir
            self.estado = "Sirviendo Tacos"  # Cambiar el estado a "Sirviendo Tacos"
            print(f"[Champion] Sirviendo tacos al Cliente {cliente_id}.")
            time.sleep(random.uniform(1, 1.5))

    # Función para cobrar
    def cobrar(self, cliente_id, pago_correcto):
        with self.lock_cobrar:  # Bloqueamos para cobrar
            self.estado = "Cobrando"  # Cambiar el estado a "Cobrando"
            time.sleep(random.uniform(1, 1.5))
            if pago_correcto:
                print(f"[Champion] Cliente {cliente_id} pagó correctamente.") # Pago correcto
                return True
            else:
                print(f"[Champion] Cliente {cliente_id} intentó pagar menos. 😠") # Pago incorrecto
                print(f"[Champion] Cliente {cliente_id} fue obligado a pagar bien. >:(")
                return False
