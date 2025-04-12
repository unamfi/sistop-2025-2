# Autor: Segura Cedeño Luisa
# SO Grupo:06

import threading
import time
import random  
import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue

# Constantes que definen los tiempos de los semáforos y los peatones
TIEMPO_VERDE = 6
TIEMPO_AMARILLO = 2
TIEMPO_PEATON = 4

# Colas utilizadas para el registro de mensajes y actualizaciones gráficas
cola_registro = queue.Queue()
cola_dibujo = queue.Queue()

def registrar_mensaje(msg):
    timestamp = time.strftime("%H:%M:%S")
    cola_registro.put(f"[{timestamp}] {msg}\n")

# Coordenadas de las intersecciones del tráfico
coordenadas_intersecciones = {
    "Intersección 1": (200, 200),
    "Intersección 2": (600, 200),
    "Intersección 3": (400, 320)  
}

estado_global_intersecciones = {}

# Clase que representa una intersección en el tráfico, gestionada por un hilo
class Interseccion(threading.Thread):
    def __init__(self, nombre, vecinos=[]):
        super().__init__()
        self.nombre = nombre
        self.estado = "NS"
        self.lock_interseccion = threading.Lock()
        self.cond_estado = threading.Condition(self.lock_interseccion)
        self.solicitud_peatonal = False
        self.emergencia = False
        self.vecinos = vecinos
        estado_global_intersecciones[self.nombre] = self.estado

    # Notifica el cambio de estado a los vecinos de la intersección
    def notificar_vecinos(self):
        estado_global_intersecciones[self.nombre] = self.estado
        registrar_mensaje(f"[{self.nombre}] Estado actualizado a {self.estado}. Vecinos: {self.vecinos}")
        cola_dibujo.put({"cmd": "actualizar_interseccion", "nombre": self.nombre, "estado": self.estado})

    # Simula el ciclo de semáforo de la intersección
    def ciclo_semaforo(self):
        with self.cond_estado:
            if self.emergencia:
                registrar_mensaje(f"[{self.nombre}] ¡MODO EMERGENCIA ACTIVADO!")
                self.estado = "EMERGENCIA"
                self.cond_estado.notify_all()
                self.notificar_vecinos()
                time.sleep(3)
                self.emergencia = False
            elif self.solicitud_peatonal:
                self.estado = "PEATON_NS" if self.estado == "NS" else "PEATON_EW"
                registrar_mensaje(f"[{self.nombre}] Fase peatonal activada: {self.estado}")
                self.cond_estado.notify_all()
                self.notificar_vecinos()
                time.sleep(TIEMPO_PEATON)
                self.solicitud_peatonal = False

    #Ejecuta el ciclo de semáforos para cada intersección
    def run(self):
        while True:
            with self.cond_estado:
                registrar_mensaje(f"[{self.nombre}] Fase {self.estado} activa. Vehículos avanzan.")
                self.notificar_vecinos()
                self.cond_estado.notify_all()
            time.sleep(TIEMPO_VERDE)

            with self.cond_estado:
                registrar_mensaje(f"[{self.nombre}] Fase amarilla.")
                self.notificar_vecinos()
            time.sleep(TIEMPO_AMARILLO)

            self.ciclo_semaforo()

            with self.cond_estado:
                if self.estado == "NS":
                    self.estado = "EW"
                elif self.estado == "EW":
                    self.estado = "NS"
                elif self.estado in ("PEATON_NS", "PEATON_EW", "EMERGENCIA"):
                    self.estado = "NS"
                registrar_mensaje(f"[{self.nombre}] Cambiando a fase {self.estado}.")
                self.notificar_vecinos()
                self.cond_estado.notify_all()

# Representa un vehículo en el tráfico, gestionado por un hilo
class Vehiculo(threading.Thread):
    contador_vehiculos = 0

    def __init__(self, nombre, ruta, es_emergencia=False):
        super().__init__()
        self.nombre = nombre
        self.ruta = ruta
        self.es_emergencia = es_emergencia
        self.id_grafico = None
        Vehiculo.contador_vehiculos += 1
        self.id_vehiculo = Vehiculo.contador_vehiculos

    #Mueve el vehículo gráficamente entre dos puntos
    def mover_grafico(self, inicio, fin):
        pasos = 20
        x0, y0 = inicio
        x1, y1 = fin
        dx = (x1 - x0) / pasos
        dy = (y1 - y0) / pasos
        for i in range(pasos):
            nuevo_x = x0 + dx * (i + 1)
            nuevo_y = y0 + dy * (i + 1)
            cola_dibujo.put({"cmd": "mover_vehiculo", "id": self.id_vehiculo, "x": nuevo_x, "y": nuevo_y})
            time.sleep(0.1)
        cola_dibujo.put({"cmd": "eliminar_vehiculo", "id": self.id_vehiculo})

    # Ejecuta el movimiento del vehículo entre las intersecciones
    def run(self):
        for interseccion in self.ruta:
            tipo = "EMERGENCIA" if self.es_emergencia else "NORMAL"
            registrar_mensaje(f"Vehículo {self.nombre} ({tipo}) se aproxima a {interseccion.nombre}.")
            with interseccion.cond_estado:
                if self.es_emergencia:
                    interseccion.emergencia = True
                    interseccion.cond_estado.notify_all()
                while interseccion.estado.startswith("PEATON"):
                    registrar_mensaje(f"Vehículo {self.nombre} espera en {interseccion.nombre}.")
                    interseccion.cond_estado.wait(timeout=1)
            with interseccion.lock_interseccion:
                registrar_mensaje(f"Vehículo {self.nombre} está cruzando {interseccion.nombre}.")
                coord_inicio = coordenadas_intersecciones[interseccion.nombre]
                destino = coord_inicio
                indice = self.ruta.index(interseccion)
                if indice + 1 < len(self.ruta):
                    destino = coordenadas_intersecciones[self.ruta[indice + 1].nombre]
                else:
                    destino = (coord_inicio[0] + 100, coord_inicio[1])
                cola_dibujo.put({
                    "cmd": "crear_vehiculo",
                    "id": self.id_vehiculo,
                    "nombre": self.nombre,
                    "x": coord_inicio[0],
                    "y": coord_inicio[1],
                    "color": "red" if self.es_emergencia else "blue"
                })
                self.mover_grafico(coord_inicio, destino)
                registrar_mensaje(f"Vehículo {self.nombre} ha cruzado {interseccion.nombre}.")
            time.sleep(random.uniform(0.5, 2))
        registrar_mensaje(f"Vehículo {self.nombre} ha completado su ruta.")

# Clase que representa un peatón que cruza la interseccion
class Peaton(threading.Thread):
    def __init__(self, nombre, interseccion):
        super().__init__()
        self.nombre = nombre
        self.interseccion = interseccion

    def run(self):
        registrar_mensaje(f"Peatón {self.nombre} solicita cruzar en {self.interseccion.nombre}.")
        with self.interseccion.cond_estado:
            self.interseccion.solicitud_peatonal = True
            self.interseccion.cond_estado.notify_all()
        cola_dibujo.put({"cmd": "crear_peaton", "nombre": self.nombre, "interseccion": self.interseccion.nombre, "color": "green"})
        time.sleep(TIEMPO_PEATON + random.uniform(0.5, 1.5))
        cola_dibujo.put({"cmd": "eliminar_peaton", "nombre": self.nombre})
        registrar_mensaje(f"Peatón {self.nombre} ha cruzado en {self.interseccion.nombre}.")

def simulacion_principal():
    inter1 = Interseccion("Intersección 1", vecinos=["Intersección 2", "Intersección 3"])
    inter2 = Interseccion("Intersección 2", vecinos=["Intersección 1", "Intersección 3"])
    inter3 = Interseccion("Intersección 3", vecinos=["Intersección 1", "Intersección 2"])
    for inter in [inter1, inter2, inter3]:
        inter.daemon = True
        inter.start()

    vehiculos = []
    for i in range(10):
        rutas_posibles = [[inter1, inter2], [inter2, inter1], [inter1, inter3], [inter3, inter1], [inter2, inter3], [inter3, inter2]]
        ruta = random.choice(rutas_posibles)
        es_emergencia = random.random() < 0.2
        veh = Vehiculo(f"V{i+1}", ruta, es_emergencia)
        vehiculos.append(veh)
        time.sleep(random.uniform(0.3, 1))
        veh.start()

    for i in range(5):
        interseccion = random.choice([inter1, inter2, inter3])
        Peaton(f"P{i+1}", interseccion).start()

class SimuladorTraficoGUI:
    # Simulación en la interfaz gráfica
    def __init__(self, master):
        self.master = master
        master.title("Simulador de Tráfico")
        master.geometry("900x700")

        tk.Label(master, text="Simulador de Tráfico con 3 Intersecciones", font=("Arial", 16)).pack()
        self.boton_iniciar = tk.Button(master, text="Iniciar Simulación", font=("Arial", 14), command=self.iniciar_simulacion)
        self.boton_iniciar.pack(pady=10)

        self.boton_detener = tk.Button(master, text="Detener Simulación", font=("Arial", 14), command=self.detener_simulacion)
        self.boton_detener.pack(pady=5)

        self.lienzo = tk.Canvas(master, width=850, height=400, bg="lightgray")
        self.lienzo.pack()

        self.registro = scrolledtext.ScrolledText(master, height=10)
        self.registro.pack(fill="both", expand=True)

        self.intersecciones_items = {}
        self.vehiculos_items = {}
        self.peatones_items = {}

        self.dibujar_intersecciones()
        self.master.after(100, self.procesar_dibujos)
        self.master.after(100, self.procesar_registro)

    def dibujar_intersecciones(self):
        for nombre, (x, y) in coordenadas_intersecciones.items():
            id_circulo = self.lienzo.create_oval(x-25, y-25, x+25, y+25, fill="green")
            id_texto = self.lienzo.create_text(x, y, text=nombre)
            self.intersecciones_items[nombre] = id_circulo

    def procesar_dibujos(self):
        while not cola_dibujo.empty():
            cmd = cola_dibujo.get()
            if cmd["cmd"] == "actualizar_interseccion":
                color = "green" if cmd["estado"] == "NS" else "orange" if cmd["estado"] == "EW" else "red"
                self.lienzo.itemconfig(self.intersecciones_items[cmd["nombre"]], fill=color)
            elif cmd["cmd"] == "crear_vehiculo":
                self.vehiculos_items[cmd["id"]] = self.lienzo.create_oval(cmd["x"]-5, cmd["y"]-5, cmd["x"]+5, cmd["y"]+5, fill=cmd["color"])
            elif cmd["cmd"] == "mover_vehiculo":
                if cmd["id"] in self.vehiculos_items:
                    x, y = cmd["x"], cmd["y"]
                    self.lienzo.coords(self.vehiculos_items[cmd["id"]], x-5, y-5, x+5, y+5)
            elif cmd["cmd"] == "eliminar_vehiculo":
                self.lienzo.delete(self.vehiculos_items.get(cmd["id"], None))
            elif cmd["cmd"] == "crear_peaton":
                x, y = coordenadas_intersecciones[cmd["interseccion"]]
                idp = self.lienzo.create_rectangle(x-8, y+30, x+8, y+45, fill=cmd["color"])
                self.peatones_items[cmd["nombre"]] = idp
            elif cmd["cmd"] == "eliminar_peaton":
                self.lienzo.delete(self.peatones_items.get(cmd["nombre"], None))
        self.master.after(100, self.procesar_dibujos)

    def procesar_registro(self):
        while not cola_registro.empty():
            msg = cola_registro.get()
            self.registro.insert(tk.END, msg)
            self.registro.see(tk.END)
        self.master.after(200, self.procesar_registro)

    def iniciar_simulacion(self):
        self.boton_iniciar.config(state="disabled")
        threading.Thread(target=simulacion_principal, daemon=True).start()

    def detener_simulacion(self):
        if messagebox.askokcancel("Confirmar", "¿Deseas detener la simulación?"):
            self.master.destroy()

# Ejecutar interfaz
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorTraficoGUI(root)
    root.mainloop()
