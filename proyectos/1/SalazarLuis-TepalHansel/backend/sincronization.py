import threading
import time
import tkinter as tk
import random
import queue
numWorkers=3
contador=0
mutexContador=threading.Semaphore(1)
TrabajadorSleep=[threading.Semaphore(0) for _ in range(numWorkers)]
TrabajadorActivo=[threading.Semaphore(0) for _ in range(numWorkers)]
mutexAtendiendo=[threading.Semaphore(1) for _ in range(numWorkers)]
alumnoRendevous=[threading.Semaphore(0) for _ in range(numWorkers)]
available=queue.Queue()

for i in range(numWorkers):
    available.put(i)

capacityAlumnos=threading.Semaphore(numWorkers)
verticalDes=10

class AlumnoSprite:
    def __init__(self,canvas,leftUpperCorner,rightBottomCorner,id):
        self.canvas=canvas
        self.setImage(canvas,leftUpperCorner,rightBottomCorner)
        self.colors=["red","yellow","blue","green","orange","purple"]
        self.headId=0
        self.bodyId=0
        self.textId=0
        self.id=id

    def setImage(self,canvas,leftUpperCorner,rightBottomCorner):
        self.canvas=canvas
        self.leftUpperCorner=leftUpperCorner
        self.rightBottomCorner=rightBottomCorner
        self.width,self.height=tuple(rightBottomCorner[i]-leftUpperCorner[i] for i in range(len(leftUpperCorner)))
        self.widthHead=self.width
        self.heightHead=self.height/2
        self.circleLeftUpperCorner=self.leftUpperCorner
        self.circleRightBottomCorner=(self.leftUpperCorner[0]+self.widthHead,self.leftUpperCorner[1]+self.heightHead)
        self.widthBody=self.width
        self.heightBody=self.height-self.heightHead
        self.bodyLeftUpperCorner=(self.rightBottomCorner[0]-self.widthBody,self.rightBottomCorner[1]-self.heightBody)
        self.bodyRightBottomCorner=self.rightBottomCorner

    def build(self):
        self.headId=self.canvas.create_oval(
            *self.circleLeftUpperCorner,
            *self.circleRightBottomCorner,
            fill="pink",
            outline="black",
            width=2
        )
        self.bodyId=self.canvas.create_rectangle(
            *self.bodyLeftUpperCorner,
            *self.bodyRightBottomCorner,
            fill=self.colors[random.randint(0,len(self.colors)-1)],
            outline="black",
            width=2
        )
        centerX=(self.bodyLeftUpperCorner[0]+self.bodyRightBottomCorner[0])/2
        centerY=(self.bodyLeftUpperCorner[1]+self.bodyRightBottomCorner[1])/2
        self.textId=self.canvas.create_text(
            centerX,centerY,
            text=f"{self.id}",
            font=("Arial",10,"bold")
        )
    def delete(self):
        self.canvas.delete(self.bodyId)
        self.canvas.delete(self.headId)
        self.canvas.delete(self.textId)
        
class Query:
    def __init__(self,id,**args):
        self.id=id
        self.args=args

    def begin(self):
        if(self.id==1):
            self.args["canvas"].itemconfig(self.args["worker"],fill="white")
        elif(self.id==2):
            self.args["canvas"].itemconfig(self.args["worker"],fill="red")
        elif(self.id==3):
            self.args["alumno"].build()
        else:
            self.args["alumno"].delete()

        

def workers(id,queries=None,worker=None,canvas=None):
    while True:
        if __name__=="__main__":
            print(f"Soy el trabajador {id} y no tengo nada que hacer")
            TrabajadorSleep[id].acquire()
            print(f"Atendiendo {id}")
            TrabajadorActivo[id].acquire()

        else:
            queries.put(Query(1,canvas=canvas,worker=worker))
            TrabajadorSleep[id].acquire()
            queries.put(Query(2,canvas=canvas,worker=worker))
            alumnoRendevous[id].release()
            TrabajadorActivo[id].acquire()
        
def alumnos(queries=None,workers=None,canvas=None,coords=None):
    global verticalDes
    global available
    global contador
    with mutexContador:
        contador+=1
        idAlumno=contador
    
    if __name__=="__main__":
        idWorker=available.get(block=True,timeout=None)
        print(f"Es el turno de {idAlumno}, pasa a {idWorker}")
        TrabajadorSleep[idWorker].release()
        print(f"{idAlumno} recibio su pedido")
        TrabajadorActivo[idWorker].release()
        print(f"Se libera {idWorker}")
        available.put(idWorker)

    else:
        idWorker=available.get(block=True,timeout=None)
        with mutexAtendiendo[idWorker]:
            newCor=coords[idWorker].copy()
        newCor[1]+=verticalDes
        newCor[3]+=verticalDes
        alumno=AlumnoSprite(canvas,(newCor[0],newCor[1]),(newCor[0]+20,newCor[1]+20),idAlumno)
        queries.put(Query(3,alumno=alumno))
        TrabajadorSleep[idWorker].release()
        alumnoRendevous[idWorker].acquire()
        time.sleep(random.uniform(0.01, 0.1))
        queries.put(Query(4,alumno=alumno))
        TrabajadorActivo[idWorker].release()
        available.put(idWorker)

if __name__=="__main__":
    for i in range(numWorkers):
        threading.Thread(target=workers,args=[i]).start()
    while True:
        threading.Thread(target=alumnos,args=[]).start()
    


    

        



