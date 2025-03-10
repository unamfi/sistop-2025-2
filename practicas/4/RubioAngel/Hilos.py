import threading
import time

# Función que ejecutará el hilo
def contar(nombre, n):
    with open("resultado.txt", "a") as f:
        for i in range(1, n+1):
            mensaje = f"{nombre} cuenta: {i}\n"
            print(mensaje, end="")
            f.write(mensaje)
            time.sleep(0.5)

# Crear dos hilos
hilo1 = threading.Thread(target=contar, args=("Hilo 1", 5))
hilo2 = threading.Thread(target=contar, args=("Hilo 2", 5))

# Iniciar los hilos
hilo1.start()
hilo2.start()

# Esperar a que los hilos terminen
hilo1.join()
hilo2.join()
#Agregamos solo un comentario para que se visualice
print("Comentario")
print("Tarea finalizada. Revisa 'resultado.txt'.")
