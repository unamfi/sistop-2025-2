from Platos import *
import pygame

ANCHO, ALTO = 800, 500
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Zona reservada con hilos activos")
clock = pygame.time.Clock()

# Zona reservada
ZONA_H = 200
ZONA_Y = ALTO - ZONA_H
ZONA_W = ANCHO
CUADRO = 180
NUM_SLOTS = 10  # Máximo 10 slots (y 10 hilos)
slots = [None] * NUM_SLOTS

lock = threading.Lock()

# Cargar fondo
imagen_fondo = pygame.image.load("assets/fondoChamps.png").convert()
imagen_fondo = pygame.transform.scale(imagen_fondo, (ANCHO, ALTO))

# Heredamos de la clase Thread
class Cliente(threading.Thread):
    # Constructor
    def __init__(self, id, champion, platos):
        super().__init__(daemon=True) # Llamamos al constructor del padre y marcamos el hilo como daemon
        self.id = id # Asignamos el id del cliente
        self.champion = champion # Mandamos al champion
        self.platos = platos # Mandamos los platos
        self.etapa = 0  # 0: no ha pedido, 1: pidió, 2: comió
        self.max_intentos = 3 # Si hace algo mal, puede volver a intentar comprar máximo 3 veces

        # Imagen del cliente
        num = random.randint(1, 3)
        path = f"assets/Esperando{num}.png" # Ubicacion del Asset
        img = pygame.image.load(path).convert_alpha() # Cargamos
        self.image = pygame.transform.scale(img, (180, 180)) # Escalamos

        self.slot_index = None # Índice de slot en pantalla
        self.estado = "esperando"  # Estado inicial como 'esperando'
        
        # Lugares para comer
        self.slots = slots
        # Bloqueo para el arreglo de Lugares
        self.lock = lock

    # Ejecución del hilo
    def run(self):
        intentos = 0
        # Mientras esté dentro de sus intentos permitidos, ejecutamos
        while intentos < self.max_intentos:
            intentos += 1 # Incrementamos un intento
            print(f"[Cliente {self.id}] Intento #{intentos}")

            # Intento de desorden (Más adelante lo haremos por etapas)
            if random.random() < 0.1: # 10% de probabilidad
                print(f"[Cliente {self.id}] Intentó hacer trampa (desorden). Rechazado.")
                self.esperarReintento() # Mandar a esperar un reintento
                continue

            # Paso 1: Pedir
            self.champion.servir_tacos(self.id)
            self.estado = "esperando"  # El cliente espera por un plato
            self.actualizar_imagen()  # Actualizamos su imagen

            # Paso 2: Comer
            print(f"[Cliente {self.id}] Esperando un plato...")
            self.platos.tomar(self.id)  # Bloquea hasta que consiga plato

            self.estado = "comiendo"  # El cliente comienza a comer
            self.actualizar_imagen() # Actualizamos su imagen
            print(f"[Cliente {self.id}] Comiendo tacos.")
            
            # Buscamos si hay un lugar disponible y seleccionamos al azar
            with self.lock:
                disponibles = [i for i, v in enumerate(self.slots) if v is None]
                if disponibles:
                    self.slot_index = random.choice(disponibles)
                    self.slots[self.slot_index] = self # Nos insertamos en el arreglo de lugares
                num = random.randint(1, 8)
                path = f"assets/Comiendo{num}.png"
                img = pygame.image.load(path).convert_alpha() # Cambiamos la imagen
                self.image = pygame.transform.scale(img, (180, 180))

            time.sleep(random.uniform(3.5, 6))

            with self.lock:
                if self.slot_index is not None:
                    self.slots[self.slot_index] = None
                    self.slot_index = None

            self.platos.devolver()  # Devolvemos el plato

            # Paso 3: Pagar (quizá mal)
            self.estado = "pagando" # Cambiamos de estado
            pago_correcto = random.random() > 0.15  # 85% de probabilidad de pagar la cantidad correcta
            pago_aceptado = self.champion.cobrar(self.id, pago_correcto)
            num = random.randint(1, 8)
            path = f"assets/Pago{num}.png"
            img = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(img, (180, 180))

            # Condicional para el pago
            if pago_aceptado:
                print(f"[Cliente {self.id}] Completó su visita con éxito. ✅\n")
                time.sleep(random.uniform(3.5, 6))
                self.estado = "apagado"  # El cliente termina su visita
                self.actualizar_imagen() # Actualizamos su imagen
                return
            else:
                self.esperarReintento()  # Enviar a reintento

        # Si llegamos a la cantidad máxima, el hilo se detiene
        print(f"[Cliente {self.id}] Fue expulsado por intentos fallidos. ❌")
        self.estado = "apagado"  # El cliente se apaga tras fallar en los intentos
        self.actualizar_imagen()

    # Función para esperar el reintento
    def esperarReintento(self):
        wait_time = random.uniform(5, 6)
        print(f"[Cliente {self.id}] Esperando {wait_time:.2f}s para reintentar...\n")
        num = random.randint(1, 3)
        path = f"assets/Esperando{num}.png"
        self.estado = "esperando" # Cambiamos el estado a esperando
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (180, 180)) # Cambiamos la imagen
        time.sleep(wait_time)

    # Función para actualizar la imagen
    def actualizar_imagen(self):
        if self.estado == "esperando":
            num = random.randint(1, 3)
            path = f"assets/Esperando{num}.png"
        elif self.estado == "comiendo":
            num = random.randint(1, 8)
            path = f"assets/Comiendo{num}.png"
        elif self.estado == "apagado" or self.estado == "pagando":
            num = random.randint(1, 3)
            path = f"assets/Pago{num}.png"
        
        img = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(img, (180, 180))
