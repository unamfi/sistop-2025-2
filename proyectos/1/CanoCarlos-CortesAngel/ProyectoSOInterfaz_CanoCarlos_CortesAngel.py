# -*- coding: utf-8 -*-
#Proyecto 1 SO Cano Nieto Carlos Arturo y Cortes Bolaños Angel David

import tkinter as tk
from tkinter import ttk
import threading
import time
import random

# Capacidad máxima del sistema eléctrico (unidades de consumo)
MAX_CONSUMO = 20
consumo_actual = 0
mutex_consumo = threading.Lock() # Protege la variable consumo_actual
sem_consumo = threading.Semaphore(MAX_CONSUMO) # Semáforo de consumo eléctrico
event_ropa_lavada = threading.Event() # La ropa debe estar lavada antes de secar

# Consumo de cada electrodoméstico
consumo_electro = {
    "Lavadora": 7,
    "Secadora": 6,
    "Microondas": 3,
    "Televisión": 5,
    "Cafetera": 3,
    "Licuadora": 4,
    "Estufa": 8,
    "Plancha": 2
}

#Mutex para electrodomésticos (conjunto)
mutex_electro = {e: threading.Lock() for e in consumo_electro}

#Diseño de la interfaz gráfica
class SimuladorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Consumo Eléctrico")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f4f8")

        self.titulo = tk.Label(root, text="Simulador de Consumo Eléctrico Doméstico", font=("Helvetica", 18, "bold"), bg="#f0f4f8", fg="#333")
        self.titulo.pack(pady=20)
        self.label_personas = tk.Label(root, text="Número de personas en la casa: 5", font=("Arial", 12), bg="#f0f4f8", fg="#333")
        self.label_personas.pack(pady=5)


        self.barra = ttk.Progressbar(root, length=600, maximum=MAX_CONSUMO)
        self.barra.pack(pady=10)

        self.label_consumo = tk.Label(root, text="Consumo actual: 0 / 20", font=("Arial", 12), bg="#f0f4f8")
        self.label_consumo.pack(pady=5)

        self.log = tk.Text(root, height=15, width=90, bg="#ffffff", fg="#222", font=("Consolas", 10), relief="groove", borderwidth=2)
        self.log.pack(pady=10)

        self.boton = ttk.Button(root, text="Iniciar Simulación", command=self.iniciar_simulacion)
        self.boton.pack(pady=10)

    def loggear(self, mensaje):
        self.log.insert(tk.END, mensaje + "\n")
        self.log.see(tk.END)

    def actualizar_consumo(self, consumo):
        global consumo_actual
        with mutex_consumo:
            consumo_actual += consumo
            self.barra['value'] = consumo_actual
            self.label_consumo.config(text=f"Consumo actual: {consumo_actual} / {MAX_CONSUMO}")

    def liberar_consumo(self, consumo):
        global consumo_actual
        with mutex_consumo:
            consumo_actual -= consumo
            self.barra['value'] = consumo_actual
            self.label_consumo.config(text=f"Consumo actual: {consumo_actual} / {MAX_CONSUMO}")

    def adquirir_consumo(self, consumo):
        for _ in range(consumo):
            sem_consumo.acquire()
        self.actualizar_consumo(consumo)

    #Libera semáforo y consumo
    def liberar_y_release(self, consumo):
        self.liberar_consumo(consumo)
        for _ in range(consumo):
            sem_consumo.release()

    def tarea(self, nombre, electro, evento_prev=None, evento_post=None):
        #Espera evento si es necesario
        if evento_prev:
            evento_prev.wait()

        # Usa el electrodoméstico protegido por mutex
        self.adquirir_consumo(consumo_electro[electro])
        with mutex_electro[electro]:
            self.loggear(f"{nombre} está usando {electro}...")
            time.sleep(random.randint(1, 3))
            self.loggear(f"{nombre} terminó de usar {electro}.")
            if evento_post:
                evento_post.set()
        self.liberar_y_release(consumo_electro[electro])
        
    def persona(self, nombre): #Simulación inquilino
        tareas = [
            #Lambda que hace que una persona ejecute una tarea
            lambda: self.tarea(nombre, "Lavadora", None, event_ropa_lavada),
            lambda: self.tarea(nombre, "Secadora", event_ropa_lavada),
            lambda: self.tarea(nombre, "Microondas"),
            lambda: self.tarea(nombre, "Televisión"),
            lambda: self.tarea(nombre, "Cafetera"),
            lambda: self.tarea(nombre, "Licuadora"),
            lambda: self.tarea(nombre, "Estufa"),
            lambda: self.tarea(nombre, "Plancha")
        ]
        random.shuffle(tareas)
        for tarea in tareas:
            tarea()
            time.sleep(1)

    #Función que espera que terminen todos los hilos
    def esperar_finalizacion(self, hilos):
        for h in hilos:
            h.join()
        self.loggear("Simulación terminada.")
        self.boton.config(state="normal")

    #Botón de inicio de la simulación
    def iniciar_simulacion(self):
        self.boton.config(state="disabled")
        hilos = [threading.Thread(target=self.persona, args=(f"Persona {i+1}",)) for i in range(5)]
        for h in hilos:
            h.start()
        threading.Thread(target=self.esperar_finalizacion, args=(hilos,), daemon=True).start()

#Ejecución del programa
if __name__ == "__main__":
    root = tk.Tk()
    app = SimuladorGUI(root)
    root.mainloop()

