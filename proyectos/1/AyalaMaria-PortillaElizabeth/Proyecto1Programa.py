import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import threading
import queue
import time
import random

class Laboratorio:
    def __init__(self, num_mesas, callback_actualizar, callback_finalizar, callback_log):
        self.total_mesas = num_mesas # Inicializa el laboratorio con el número total de mesas
        self.mesas_funcionales = random.randint(1, num_mesas) # Mesas disponibles aleatorias
        self.mesas = {i: [] for i in range(1, self.mesas_funcionales + 1)} # Diccionario de mesas con listas de alumnos
        self.historial_mesas = {i: 0 for i in range(1, self.mesas_funcionales + 1)} # Historial para registrar cuántos alumnos usaron cada mesa
        self.max_alumnos_por_mesa = 3
        self.max_espera = 6
        self.alumnos_espera = queue.Queue(self.max_espera) # Cola para los alumnos en espera
        self.jefe_presente = threading.Event() # Evento para controlar si el jefe esta presente o no
        self.jefe_presente.set() # El jefe inicia presente (estando en el laboratorio)
        self.lock = threading.Lock() # Bloque para evitar condiciones de carrera
        self.alumnos_activos = [] # Lista para hacer un seguimiento de los alumnos en el laboratorio 
        self.jefe_trabajando = True # Controla si el jefe sigue operando (se ha ido a comer)
        self.callback_actualizar = callback_actualizar # Actualizar la interfaz grafica
        self.callback_finalizar = callback_finalizar # Finalizar simulacion
        self.callback_log = callback_log  # Registrar eventos en la interfaz      
        


    def alumno_intenta_entrar(self, nombre): # Método para que un alumno intente entrar al laboratorio
        while self.jefe_trabajando: 
            if not self.jefe_presente.is_set():
                if self.alumnos_espera.full():
                    self.callback_log(f"{nombre} no puede esperar y se va.")
                    return
                self.callback_log(f"{nombre} está esperando en la fila de entrada.") # El alumno se pone en la fila de espera
                self.alumnos_espera.put(nombre)
                return
            else:
                self.asignar_mesa(nombre) # Si el jefe está presente, intenta asignar una mesa al alumno
                return

    def asignar_mesa(self, nombre):
        with self.lock: # Permite controlar el acceso
            for mesa, alumnos in self.mesas.items():
                if len(alumnos) < self.max_alumnos_por_mesa: # Si la mesa tiene espacio
                    alumnos.append(nombre)
                    self.historial_mesas[mesa] += 1 # Registrar uso de mesa
                    self.alumnos_activos.append(nombre) # Añadir alumno a lista de activos
                    self.callback_log(f"{nombre} ha tomado un lugar en la mesa {mesa}.")
                    self.callback_actualizar()
                    threading.Thread(target=self.uso_mesa, args=(nombre, mesa)).start()  # Inicia un hilo para simular el uso de la mesa
                    return
        self.callback_log(f"{nombre} no encontró mesa y se va.") # Si no hay mesas disponibles, el alumno se va

    def uso_mesa(self, nombre, mesa):
        tiempo = random.randint(6, 12)
        time.sleep(tiempo) # Simula el tiempo de uso de la mesa
        with self.lock: # Bloquea el acceso a recursos compartidos
            self.mesas[mesa].remove(nombre) # Elimina al alumno de la mesa
            self.alumnos_activos.remove(nombre) # Eliminar de la lista de activos
        self.callback_log(f"{nombre} ha dejado la mesa {mesa} después de {tiempo} minutos.")
        self.callback_actualizar()

    def jefe_se_va_a_comer(self):
        while self.jefe_trabajando: 
            time.sleep(random.randint(10, 20))  # Intervalo antes de que el jefe se vaya
            if not self.jefe_trabajando: # Si el jefe ya no está trabajando (simulación terminada), rompe el ciclo
                break  
            self.jefe_presente.clear() # Indica que el jefe no está presente
            with self.lock:
                self.callback_log(f"El jefe se ha ido a comer. Actualmente hay {len(self.alumnos_activos)} alumnos dentro del laboratorio.")
            time.sleep(random.randint(5, 10))  # Simula el tiempo de comida
            if not self.jefe_trabajando: # Si el jefe ya no está trabajando (simulación terminada), rompe el ciclo
                break  # Verifica de nuevo antes de volver
            self.jefe_presente.set() # Indica que el jefe ha regresado
            self.callback_log("El jefe ha regresado. Los alumnos en espera pueden entrar.")
            while not self.alumnos_espera.empty(): # Asigna mesas a los alumnos en espera
                self.asignar_mesa(self.alumnos_espera.get())

    def esperar_a_que_terminen(self):
        while self.alumnos_activos or not self.alumnos_espera.empty():  # Esperar a que todos los alumnos terminen
            time.sleep(1)
        self.jefe_trabajando = False # Finaliza el turno del jefe
        self.callback_finalizar()

class LaboratorioGUI:
    def __init__(self, root, num_mesas):
        self.root = root
        self.root.title("Simulación del Laboratorio")
        
        
        # Crea una instancia de la clase Laboratorio, pasando las funciones de callback para actualizar la interfaz,
        # finalizar la simulación y registrar eventos.
        self.laboratorio = Laboratorio(num_mesas, self.actualizar_interfaz, self.finalizar_simulacion, self.log_evento)
        self.labels_mesas = {} # Diccionario para almacenar las etiquetas de las mesas en la interfaz gráfica.

        self.label_funcionando = tk.Label(root, text=f"Mesas funcionales hoy: {self.laboratorio.mesas_funcionales}") # Etiqueta que muestra cuántas mesas funcionales hay hoy.
        self.label_funcionando.pack() 

        self.label_estado_jefe = tk.Label(root, text="Estado del jefe: Presente", fg="green") # Etiqueta que muestra el estado del jefe (presente o comiendo).
        self.label_estado_jefe.pack() 

        self.frame_mesas = tk.Frame(root) # Contenedor para las etiquetas de las mesas.
        self.frame_mesas.pack() 

        for i in range(1, self.laboratorio.mesas_funcionales + 1): # Crea etiquetas para cada mesa funcional y las agrega al contenedor.
            lbl = tk.Label(self.frame_mesas, text=f"Mesa {i}: libre", relief="groove", width=35, height=2, bg="#f0f0f0")
            lbl.grid(row=(i-1) // 3, column=(i-1) % 3, padx=6, pady=6) # Posiciona las etiquetas en una cuadrícula.
            self.labels_mesas[i] = lbl

        self.lista_alumnos = tk.Listbox(root, height=10, width=40) # Lista que muestra los alumnos activos en el laboratorio.
        self.lista_alumnos.pack(pady=10)

        self.label_espera = tk.Label(root, text="En espera: 0 alumnos") # Etiqueta que muestra cuántos alumnos están en espera.
        self.label_espera.pack()

        self.consola = ScrolledText(root, height=10, width=60, state="disabled", wrap="word") # Consola de texto para registrar eventos 
        self.consola.pack(pady=10)

        self.btn_iniciar = tk.Button(root, text="Iniciar Simulación", command=self.iniciar_simulacion) # Botón para iniciar la simulación
        self.btn_iniciar.pack(pady=10)

        self.root.after(1000, self.actualizar_interfaz)  #Programa una actualización periódica de la interfaz gráfica.

    def log_evento(self, texto): # Método para registrar eventos en la consola de texto.
        self.consola.config(state="normal")
        self.consola.insert(tk.END, texto + "\n")
        self.consola.see(tk.END)
        self.consola.config(state="disabled")

    def actualizar_interfaz(self):
        for mesa, alumnos in self.laboratorio.mesas.items(): # Actualiza el texto de cada etiqueta de mesa según los alumnos asignados.
            texto = f"Mesa {mesa}: " + ", ".join(alumnos) if alumnos else f"Mesa {mesa}: libre"
            self.labels_mesas[mesa].config(text=texto)

        self.lista_alumnos.delete(0, tk.END) # Actualiza la lista de alumnos activos.
        for alumno in self.laboratorio.alumnos_activos:
            self.lista_alumnos.insert(tk.END, alumno)

        self.label_espera.config(text=f"En espera: {self.laboratorio.alumnos_espera.qsize()} alumnos") # Actualiza la etiqueta de alumnos en espera.

        if self.laboratorio.jefe_presente.is_set(): # Actualiza el estado del jefe (presente o comiendo).
            self.label_estado_jefe.config(text="Estado del jefe: Presente", fg="green")
        else:
            self.label_estado_jefe.config(text="Estado del jefe: Comiendo", fg="red")

    def iniciar_simulacion(self):
        self.btn_iniciar.config(state="disabled")
        threading.Thread(target=self.laboratorio.jefe_se_va_a_comer, daemon=True).start() # Inicia un hilo para simular que el jefe se va a comer.
        alumnos = [f"Alumno {i+1}" for i in range(self.laboratorio.mesas_funcionales * self.laboratorio.max_alumnos_por_mesa + 5)]  # Genera una lista de alumnos que intentarán ingresar al laboratorio.
        def llegada_pausada():
            for alumno in alumnos:
                threading.Thread(target=self.laboratorio.alumno_intenta_entrar, args=(alumno,)).start() # Inicia un hilo para cada alumno que intenta ingresar.
                time.sleep(random.uniform(1.5, 3.0))
            threading.Thread(target=self.laboratorio.esperar_a_que_terminen).start()
        threading.Thread(target=llegada_pausada).start()

    def finalizar_simulacion(self):
        resumen = "\nResumen del día:\n"
        for mesa, cantidad in self.laboratorio.historial_mesas.items():
            resumen += f" - Mesa {mesa}: {cantidad} alumno(s) la usaron\n"  # Agrega al resumen cuántos alumnos usaron cada mesa.
        self.log_evento("La simulación ha finalizado.") # Registra en el log que la simulación ha finalizado
        self.log_evento(resumen)  # Registra el resumen en el log.
        messagebox.showinfo("Resumen del Día", resumen) # Muestra el resumen en un cuadro de diálogo.
        self.root.after(3000, self.root.quit)


class VentanaInicio:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Configuración Inicial")
        tk.Label(self.root, text="Ingrese el número de mesas disponibles:").pack(pady=10)  # Etiqueta que solicita al usuario ingresar el número de mesas disponibles.
        self.entry = tk.Entry(self.root)
        self.entry.pack(pady=5)
        tk.Button(self.root, text="Iniciar", command=self.iniciar_simulacion).pack(pady=10)
        self.root.mainloop()

    def iniciar_simulacion(self):
        try:
            num_mesas = int(self.entry.get())
            if num_mesas < 1:
                raise ValueError
            self.root.destroy() # Si el número es válido, cierra la ventana de configuración.
            root = tk.Tk() # Crea una nueva ventana para la simulación.
            app = LaboratorioGUI(root, num_mesas)
            root.mainloop() 
        except ValueError:
            messagebox.showerror("Error", "Por favor, ingresa un número válido mayor que 0.")

if __name__ == "__main__":
    VentanaInicio()
