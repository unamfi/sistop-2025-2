#Proyecto 1 SO Cano Nieto Carlos Arturo y Cortes Bolaños Angel David

import threading
import time
import random

# Capacidad máxima del sistema eléctrico (unidades de consumo)
MAX_CONSUMO = 20
consumo_actual = 0
mutex_consumo = threading.Lock()  # Protege la variable consumo_actual
sem_consumo = threading.Semaphore(MAX_CONSUMO)  # Semáforo de consumo eléctrico

# Mutex para electrodomésticos críticos
lavadora_mutex = threading.Lock()
secadora_mutex = threading.Lock()
cafetera_mutex = threading.Lock()
licuadora_mutex = threading.Lock()
estufa_mutex = threading.Lock()
plancha_mutex = threading.Lock()

event_ropa_lavada = threading.Event()  # La ropa debe estar lavada antes de secar

def adquirir_consumo(consumo):
    # Adquirir unidades de consumo, bloquea si no hay suficiente
    for _ in range(consumo):
        sem_consumo.acquire()
    global consumo_actual
    with mutex_consumo:
        consumo_actual += consumo

def liberar_consumo(consumo):
    # Liberar unidades de consumo
    global consumo_actual
    with mutex_consumo:
        consumo_actual -= consumo
    for _ in range(consumo):
        sem_consumo.release()

# Consumo de cada electrodoméstico
consumo_electro = {
    "lavadora": 7,
    "secadora": 6,
    "microondas": 3,
    "television": 5,
    "cafetera": 3,
    "licuadora": 4,
    "estufa": 8,
    "plancha": 2
}

def usar_lavadora(persona):
    adquirir_consumo(consumo_electro["lavadora"])
    with lavadora_mutex:
        print(f"{persona} está usando la lavadora...")
        time.sleep(random.randint(2, 5))
        print(f"{persona} terminó de lavar la ropa.")
        event_ropa_lavada.set()
    liberar_consumo(consumo_electro["lavadora"])

def usar_secadora(persona):
    event_ropa_lavada.wait()
    adquirir_consumo(consumo_electro["secadora"])
    with secadora_mutex:
        print(f"{persona} está usando la secadora...")
        time.sleep(random.randint(2, 4))
        print(f"{persona} terminó de secar la ropa.")
    liberar_consumo(consumo_electro["secadora"])

def usar_microondas(persona):
    adquirir_consumo(consumo_electro["microondas"])
    print(f"{persona} está usando el microondas...")
    time.sleep(random.randint(1, 3))
    print(f"{persona} terminó de usar el microondas.")
    liberar_consumo(consumo_electro["microondas"])

def ver_tv(persona):
    adquirir_consumo(consumo_electro["television"])
    print(f"{persona} está viendo TV...")
    time.sleep(random.randint(3, 6))
    print(f"{persona} terminó de ver TV.")
    liberar_consumo(consumo_electro["television"])

def preparar_cafe(persona):
    adquirir_consumo(consumo_electro["cafetera"])
    with cafetera_mutex:
        print(f"{persona} está preparando café...")
        time.sleep(random.randint(2, 5))
        print(f"{persona} terminó de preparar café.")
    liberar_consumo(consumo_electro["cafetera"])

def usar_licuadora(persona):
    adquirir_consumo(consumo_electro["licuadora"])
    with licuadora_mutex:
        print(f"{persona} está usando la licuadora...")
        time.sleep(random.randint(1, 4))
        print(f"{persona} terminó de usar la licuadora.")
    liberar_consumo(consumo_electro["licuadora"])

def usar_estufa(persona):
    adquirir_consumo(consumo_electro["estufa"])
    with estufa_mutex:
        print(f"{persona} está cocinando en la estufa...")
        time.sleep(random.randint(3, 6))
        print(f"{persona} terminó de cocinar.")
    liberar_consumo(consumo_electro["estufa"])

def planchar(persona):
    adquirir_consumo(consumo_electro["plancha"])
    with plancha_mutex:
        print(f"{persona} está planchando ropa...")
        time.sleep(random.randint(2, 5))
        print(f"{persona} terminó de planchar.")
    liberar_consumo(consumo_electro["plancha"])

# Simulación de inquilino
def persona(nombre):
    tareas = [usar_lavadora, usar_secadora, usar_microondas, ver_tv,
              preparar_cafe, usar_licuadora, usar_estufa, planchar]
    random.shuffle(tareas)
    for tarea in tareas:
        tarea(nombre)
        time.sleep(1)

# Crear y ejecutar hilos para múltiples personas
hilos = [threading.Thread(target=persona, args=(f"Persona {i+1}",)) for i in range(6)]
for h in hilos:
    h.start()
for h in hilos:
    h.join()

print("Simulación terminada.")
