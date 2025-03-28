
import threading
import random 
import time
capacidadElevador = 5    #Capacidad elevador
numPisos=5                # Número de pisos


elevador = threading.Semaphore(0)   #Mutex del elevador, el cual evita que el elevador se mueva si nadie lo pide

mutexPisos = threading.Semaphore(1) #Protege el acceso a piso i
mutexPisosEntrada=threading.Semaphore(1)
mutexPisosSalida=threading.Semaphore(1)
pisos = [0 for _ in range(numPisos)]
bajanPiso=[0 for _ in range(numPisos)]

mutexPisosDireccion=threading.Semaphore(1)

mutexCapacidadActualElevador = threading.Semaphore(1)

#No deja entrar a más de 5 personas
multiplexCapacidadElevador=threading.Semaphore(capacidadElevador)

#Llevar la cuenta de las personas dentro del elevador
mutexCapacidadActual=threading.Semaphore(1)
capacidadActualElevador=0

#
cantidadPersonas=0
mutexCantidadPersonas=threading.Semaphore(1)

#Las personas que esperan a llegar a su piso para salir
pisosTorniqetSalida=[threading.Semaphore(0) for _ in range(numPisos)]
#Las personas que esperan a que llegue el elevador para meterse
pisosTorniqetEntrada=[threading.Semaphore(0) for _ in range(numPisos)]

arrayMutexEntrada=[threading.Semaphore(1) for _ in range(numPisos)]
arrayMutexBajada=[threading.Semaphore(1) for _ in range(numPisos)]


mutexPrint=threading.Semaphore(1)

#Direcciones
pisoDown=6
pisoDownMutex=threading.Semaphore(1)

pisoUpMutex=threading.Semaphore(1)
pisoUp=-1

#Por cada nueva persona se añade una al elevador

def asignacionPiso(id):
    global cantidadPersonas
    pisoInicial=random.randint(0,numPisos-1)
    pisoDestino=pisoInicial
    while pisoInicial == pisoDestino:
        pisoDestino=random.randint(0,numPisos-1)
    with mutexCantidadPersonas:
        cantidadPersonas+=1
    elevador.release()
    with mutexPrint:
        print(f'La persona {id} en el piso {pisoInicial} quiere ir a {pisoDestino}')
    with arrayMutexEntrada[pisoInicial]:
        pisos[pisoInicial]+=1
    llamarAscensor(id,pisoInicial, pisoDestino)
    
def llamarAscensor( id,pisoInicial, pisoDestino):
    global pisoDown
    global pisoUp
    global cantidadPersonas
    with pisoDownMutex:
        pisoDown=min(pisoDown,pisoInicial)
    with pisoUpMutex:    
        pisoUp=max(pisoUp,pisoInicial)
    pisosTorniqetEntrada[pisoInicial].acquire()
    pisosTorniqetEntrada[pisoInicial].release()
    multiplexCapacidadElevador.acquire()
    with mutexPrint:
        print(f"Estamos adentro del elevador la persona {id} Piso {pisoInicial}")
    with arrayMutexEntrada[pisoInicial]:
        pisos[pisoInicial]-=1
        if(pisos[pisoInicial]==0):
            pisosTorniqetEntrada[pisoInicial].acquire()
           
    with arrayMutexBajada[pisoDestino]:
        bajanPiso[pisoDestino]+=1
    with pisoDownMutex:
        pisoDown=min(pisoDown,pisoInicial)
    with pisoUpMutex:    
        pisoUp=max(pisoUp,pisoInicial)
    pisosTorniqetSalida[pisoDestino].acquire()
    pisosTorniqetSalida[pisoDestino].release()
    with mutexPrint:
        print(f"Gracias elevador! {id} Piso {pisoDestino}")
    with arrayMutexBajada[pisoDestino]:
        bajanPiso[pisoDestino]-=1
        if(bajanPiso[pisoDestino]==0):
            pisosTorniqetSalida[pisoDestino].acquire()
    multiplexCapacidadElevador.release()
    with mutexCantidadPersonas:
        cantidadPersonas-=1

            
def ascensor():
    dir=False
    i=0
    while True:
        #El elevador no debe moverse si no hay personas
        elevador.acquire()
        with mutexCantidadPersonas:
            if(cantidadPersonas==0):
                continue
        dir=not dir
        with mutexPrint:
            print("Ya voy para allá ciudadano promedio")
        #Direccion, intercala arriba y abajo
        #Nos estamos moviendo
        if(dir):
            while i<=pisoUp:
                with mutexPrint:
                    print(f"Elevador en el piso {i}") 
                with arrayMutexBajada[i]:
                    if(bajanPiso[i]):
                        pisosTorniqetSalida[i].release()
                with arrayMutexEntrada[i]:
                    if(pisos[i]):
                        pisosTorniqetEntrada[i].release()
                        
                i+=1    
            i-=1
        else:
            while i>=pisoDown:
                with mutexPrint:
                    print(f"Elevador en el piso {i}")
                with arrayMutexBajada[i]:
                    if(bajanPiso[i]):
                        pisosTorniqetSalida[i].release()
                with arrayMutexEntrada[i]:
                    if(pisos[i]):
                        pisosTorniqetEntrada[i].release()
                i-=1
            i+=1
        

def main():
    threading.Thread(target=ascensor).start()
    max_people = 50
    for i in range(max_people):
            threading.Thread(target=asignacionPiso, args=[i]).start()
        


main()