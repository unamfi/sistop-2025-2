import threading
import time

def tarea(nombre, tiempo):
    for i in range(5):
        print(f"{nombre} ejecutando iteración {i+1}")
        time.sleep(tiempo)
    print(f"{nombre} ha terminado.")

# Crear hilos
hilo1 = threading.Thread(target=tarea, args=("Hilo 1", 1))
hilo2 = threading.Thread(target=tarea, args=("Hilo 2", 1.5))

# Iniciar hiloss
hilo1.start()
hilo2.start()

# Esperar a que los hilos terminen
hilo1.join()
hilo2.join()

#Se hizo un comenatrio donde se aprecia el cambio 
#que se realizo al codigo 
print("Ejecución finalizada.")
