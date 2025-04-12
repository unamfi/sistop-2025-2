import tkinter as tk
from tkinter import scrolledtext, messagebox
import sys
import os
# Add the parent directory of the 'backend' folder to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import queue 
import backend.sincronization as bs
import threading
import random
import time
import math

class TiendaSprite:
    def __init__(self,canvas,leftUpperCorner,rightBottomCorner,base,diameter,dFromUpper):
        self.canvas=canvas
        self.leftUpperCorner=leftUpperCorner
        self.rightBottomCorner=rightBottomCorner
        self.base=base
        self.width=rightBottomCorner[0]-leftUpperCorner[0]
        self.height=rightBottomCorner[1]-leftUpperCorner[1]
        self.desplazamiento=self.width/2-self.base
        self.diameter=diameter
        self.dFromUpper=dFromUpper
        self.colors=["red","yellow","blue","green","orange","purple"]

    def build(self):
        workers=[]
        coords=[]
        self.canvas.create_rectangle(
                self.leftUpperCorner[0], self.leftUpperCorner[1],  # Esquina rightUpperCorner izquierda (x1, y1)
                self.rightBottomCorner[0], self.rightBottomCorner[1], # Esquina leftUpperCorner derecha (x2, y2)
                fill="white",  # Color de relleno
                outline="black",   # Color del borde
                width=2           # Grosor del borde
            )
        text_x = (self.leftUpperCorner[0] + self.rightBottomCorner[0]) / 2  # Centro horizontal del rectángulo
        text_y = self.leftUpperCorner[1] - 10  # Un poco encima del rectángulo
        self.canvas.create_text(
            text_x, text_y,
            text="DON RATA",  # Texto a mostrar
            font=("Arial", 14, "bold"),  # Fuente y tamaño
            fill="black"  # Color del texto
        )
        for i in range(bs.numWorkers):
            newX=self.leftUpperCorner[0]+self.base+self.desplazamiento*i-self.diameter/2
            newY=self.leftUpperCorner[1]+self.dFromUpper
            workers.append(
            self.canvas.create_oval(
                newX,newY,
                newX+self.diameter,newY+self.diameter,
                fill="white",  # Color de relleno
                outline="black",   # Color del borde
                width=2           # Grosor del borde
            ))
            coords.append([newX,newY,newX+self.diameter,newY+self.diameter])
        return workers,coords

    def areaAlumnos(self):
        canvas_width = 400
        canvas_height = 300
        arc_x1 = 0  # Extender el semicírculo desde el borde izquierdo
        arc_y1 = canvas_height - 150  # Ajustar para que el semicírculo esté más cerca del borde inferior
        arc_x2 = canvas_width  # Extender el semicírculo hasta el borde derecho
        arc_y2 = canvas_height + 50  # Ajustar la altura del semicírculo

        # Dibujar el semicírculo
        self.canvas.create_arc(
            arc_x1, arc_y1, arc_x2, arc_y2,
            start=0, extent=180,  
            fill="lightblue",  
            outline="black",  
            width=2  
        )

        # Dibujar alumnos dentro del semicírculo
        self.dibujar_alumnos(arc_x1, arc_y1, arc_x2, arc_y2)

    def dibujar_alumnos(self, arc_x1, arc_y1, arc_x2, arc_y2):
        """Dibuja y anima objetos de tipo alumno dentro del semicírculo."""
        num_alumnos = 5  # Número de alumnos
        radius = (arc_x2 - arc_x1) / 2 - 20  # Radio del semicírculo, ajustado para que los alumnos no se salgan
        center_x = (arc_x1 + arc_x2) / 2  # Centro en x
        center_y = arc_y2  # Centro en y (parte baja del semicírculo)
        self.alumnos = []  # Lista para almacenar las referencias de los alumnos

        for i in range(num_alumnos):
            # Ángulo para distribuir los alumnos uniformemente
            angle = (180 / (num_alumnos + 1)) * (i + 1)  # Ángulo en grados
            radian = angle * (math.pi / 180)  # Convertir a radianes

            # Calcular las coordenadas x e y usando trigonometría
            x = center_x + radius * math.cos(radian)
            y = center_y - radius * math.sin(radian)  # Usar el radio y el ángulo para calcular y

            diameter = 20  # Tamaño del círculo (cabeza)
            body_size = 20  # Tamaño del cuerpo (cuadrado)

            # Dibujar un círculo para representar la cabeza
            head = self.canvas.create_oval(
                x - diameter / 2, y - diameter / 2,
                x + diameter / 2, y + diameter / 2,
                fill="pink",  # Color de la cabeza
                outline="black",  # Borde de la cabeza
                width=1
            )

            # Dibujar un cuadrado para representar el cuerpo
            body = self.canvas.create_rectangle(
                x - body_size / 2, y + diameter / 2,  # Coordenadas superiores del cuadrado
                x + body_size / 2, y + diameter / 2 + body_size,  # Coordenadas inferiores del cuadrado
                fill=self.colors[random.randint(0,5)],  # Color del cuerpo
                outline="black",  # Borde del cuerpo
                width=1
            )

            # Guardar las referencias de la cabeza y el cuerpo
            self.alumnos.append((head, body))

        # Iniciar la animación
        self.animar_alumnos()

    def animar_alumnos(self):
        """Anima a los alumnos moviéndolos ligeramente."""
        for head, body in self.alumnos:
            # Movimiento aleatorio en x e y
            dx = random.choice([-1, 0, 1])  # Movimiento en x
            dy = random.choice([-1, 0, 1])  # Movimiento en y

            # Mover la cabeza y el cuerpo
            self.canvas.move(head, dx, dy)
            self.canvas.move(body, dx, dy)

        # Repetir la animación después de 100 ms
        self.canvas.after(100, self.animar_alumnos)
            
class TiendaApp:
    def __init__(self, root):
        self.queries=queue.Queue()
        self.root = root
        self.workers=[]
        self.coords=[]
        self.canvas = tk.Canvas(root, width=400, height=300, bg="white")
        self.canvas.pack()
        #Título de la interfaz
        self.root.title("Simulación de Tienda - Pedidos Concurrentes")
        # Interfaz gráfica
        self.setup_ui()
        # Inicio de los trabajadores
        threading.Thread(target=self.inicio,args=[],daemon=True).start()
        self.hearing()

    def inicio(self):
        for i in range(bs.numWorkers):
            threading.Thread(target=bs.workers, args=[i,self.queries,self.workers[i],self.canvas],daemon=True).start()
        while True:
            threading.Thread(target=bs.alumnos, args=[self.queries,self.workers,self.canvas,self.coords],daemon=True).start()
            time.sleep(random.uniform(0,0.05))


    def hearing(self):
        """Revisa periódicamente la cola y ejecuta las acciones en la UI."""
        try:
            #while True:  # Saca todos los disponibles
                task = self.queries.get_nowait()
                task.begin()  # Ejecuta el cambio en la UI (en el hilo principal)
        except queue.Empty:
            pass
        self.root.after(200, self.hearing)  # Vuelve a revisar en 100ms

    
    def setup_ui(self):
        # Frame principal
        frame = tk.Frame(self.root, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        # Título
        tk.Label(frame, text="🏪 Simulación de Don Rata", font=("Arial", 16)).pack(pady=5)

        tienda=TiendaSprite(canvas=self.canvas,leftUpperCorner=(50,50),rightBottomCorner=(350,100),base=30,diameter=20,dFromUpper=20)
        self.workers,self.coords=tienda.build()
        self.areaAlumnos=tienda.areaAlumnos()
        # Botón para detener la simulación
        tk.Button(frame, text="Detener Simulación", command=self.detener_simulacion).pack(pady=5)
    
    
    def detener_simulacion(self):
        """Detiene la simulación y cierra la aplicación."""
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = TiendaApp(root)
    root.mainloop()