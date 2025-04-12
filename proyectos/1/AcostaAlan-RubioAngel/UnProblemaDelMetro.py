# Acosta Jacinto Alan
# Rubio Carmona Jose Angel
# Proyecto 1: Una situación cotidiana con concurrencia y sincronización  
# Sistemas Operativos  grupo: 6 2025-2

import threading
import time
import random
from queue import Queue

NUM_MAQUINAS = 2
NUM_USUARIOS = 10

# Semáforos para las máquinas: controlan que solo un usuario acceda a cada máquina
maquinas = [threading.Semaphore(1) for _ in range(NUM_MAQUINAS)]

# Cola que mantiene el orden de llegada de los usuarios
fila = Queue()

# Condición que permite coordinar el acceso a la fila
condicion = threading.Condition()


intentos_fallidos = {i: 0 for i in range(1, NUM_USUARIOS + 1)}
usuarios_terminados = set()


def log(tipo, id_, mensaje, color="\033[94m", extra=""):
    print(f"{color}[{tipo} {id_}] \033[0m{mensaje} {extra}")

# Lógica de intento de recarga
def usar_maquina(id_usuario):
    while True:
        with condicion:
            # Espera hasta que el usuario sea el primero en la fila
            while fila.queue[0] != id_usuario:
                condicion.wait()

            # Busca una máquina disponible
            maquina_disponible = -1
            for i in range(NUM_MAQUINAS):
                if maquinas[i].acquire(blocking=False):
                    maquina_disponible = i
                    break

            # Si no hay máquina libre, vuelve a esperar
            if maquina_disponible == -1:
                condicion.wait()
                continue

            fila.get()
            condicion.notify_all()

        log("Máquina", maquina_disponible + 1, "🔄Usuario está recargando...", "\033[92m", f"\033[93m(Usuario {id_usuario})\033[0m")
        tiempo = random.uniform(1.5, 3.5)
        time.sleep(tiempo)

        if random.random() < 0.15:
            log("Máquina", maquina_disponible + 1, "❌ No aceptó la tarjeta. Volviendo a la fila...", "\033[91m", f"\033[93m(Usuario {id_usuario})\033[0m")
            maquinas[maquina_disponible].release()
            with condicion:
                fila.put(id_usuario)  # Se vuelve a formar
                intentos_fallidos[id_usuario] += 1
                condicion.notify_all()
        else:
            log("Máquina", maquina_disponible + 1, f"✅ Recargó con éxito en {tiempo:.2f}s", "\033[92m", f"\033[93m(Usuario {id_usuario})\033[0m")
            maquinas[maquina_disponible].release()
            with condicion:
                usuarios_terminados.add(id_usuario)
                condicion.notify_all()
            break  

def usuario(id_usuario):
    with condicion:
        fila.put(id_usuario)
        log("Usuario", id_usuario, "Se formó en la fila.")
        condicion.notify_all()

    usar_maquina(id_usuario)

hilos = []
for i in range(1, NUM_USUARIOS + 1):
    hilo = threading.Thread(target=usuario, args=(i,))
    hilos.append(hilo)
    hilo.start()
    time.sleep(0.5) 

for h in hilos:
    h.join()


print("\n🎉 Todos los usuarios han recargado su tarjeta, ¡Feliz viaje!\n")
print("📊 Intentos fallidos por usuario:")
for i in range(1, NUM_USUARIOS + 1):
    print(f" - Usuario {i}: {intentos_fallidos[i]}")



'''
Descripcion basica del codigo:
El codigo implementa dos maquinas de recarga para la tarjeta del metro, donde solo puede pasar
una persona a la vez, las personas deberan hacer una fila para las dos maquinas, como se vayan
desocupando las maquinas estos pasaran,el detalle es que la tarjeta puede fallar y 
lamentablemente deberan formarse de nuevo para recagar la tarjeta.
El codigo muestra el tiempo que tardaron en recargar su tarjeta, por esta vez pensemos que 1s
equivale a 10 segundos(que estres no?).
El proceso acaba hasta que todos hayan recargado su tarjeta y sean felices😄.
'''