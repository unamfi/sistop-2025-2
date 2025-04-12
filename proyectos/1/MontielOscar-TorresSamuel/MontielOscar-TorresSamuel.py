"""
Proyecto 1

Autores:
- Torres Delgadillo Samuel Mixcoatl
- Montiel Juárez Oscar Iván

Descripción:
Este proyecto modela el funcionamiento de un estacionamiento de la Facultad de Ingeniería,
donde se presentan problemas de concurrencia debido a un sistema de sobrecupo y mala gestión
de espacios. Se gestionan vehículos que llegan al estacionamiento, los cuales pueden ocupar
espacios de forma normal o equivocada (ocupando dos espacios). Una grúa se encarga de retirar
a los vehículos mal estacionados. El sistema utiliza hilos con sincronización basada en semáforos,
mutex y variables de condición, y presenta una interfaz gráfica en tiempo real utilizando la
biblioteca Rich. Además, se guarda un historial de eventos en un archivo de texto.

REQUISITO
instalar rich: pip install rich
"""

import threading
import time
import random
from rich.console import Console
from rich.table import Table
from rich.live import Live

capacidadFisica = 15
sobreCupo = 20
espacios = {f"A{i}": False for i in range(1, capacidadFisica + 1)}
mutexEspacios = threading.Lock()
condicionEspacio = threading.Condition(mutexEspacios)
semaforo = threading.Semaphore(sobreCupo)
registroEventos = []
asignacionVehiculos = {}
consola = Console(width=120)

stop_event = threading.Event()

def guardarHistorial():
    """
    guarda el historial en un txt

    mantiene el historial actualizado de los eventos del 
    estacionamiento y actualiza el archivo "historial.txt" cada segundo
    """
    while not stop_event.is_set():
        with mutexEspacios:
            with open("historial.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(registroEventos[-50:]))
        time.sleep(1)

def ocuparDosEspacios(idVehiculo):
    """I
    intenta ocupar dos espacios consecutivos
    para un vehículo que se estaciona mal

    Args:
        idVehiculo (int): identificador del vehículo

    Returns:
        bool: True si se asignaron dos espacios exitosamente, False sino
    """
    with condicionEspacio:
        for i in range(1, capacidadFisica):
            espacio1 = f"A{i}"
            espacio2 = f"A{i+1}"
            if not espacios[espacio1] and not espacios[espacio2]:
                espacios[espacio1] = True
                espacios[espacio2] = True
                asignacionVehiculos[idVehiculo] = (espacio1, espacio2)
                registroEventos.append(f"Carro {idVehiculo} OCUPÓ MAL {espacio1} y {espacio2}")
                return True
        return False

def vehiculoLlegada(idVehiculo):
    """
    controla la llegada de un vehículo al estacionamiento, le asigna un espacio

    dependiendo de una probabilidad, intenta asignar dos espacios consecutivos 
    o un solo espacio
     
    utiliza mecanismos de sincronización  y espera
    activamente en caso de no haber espacios disponibles

    Args:
        idVehiculo (int): Identificador del vehículo.
    """
    try:
        if random.random() < 0.05:
            if semaforo._value >= 2:
                semaforo.acquire(2)
                if not ocuparDosEspacios(idVehiculo):
                    semaforo.release(2)
                    raise Exception("Espacio doble no disponible")
            else:
                raise Exception("No hay permisos para estacionamiento doble")
        else:
            semaforo.acquire()
            
        with condicionEspacio:
            while True:
                espacios_libres = [e for e, libre in espacios.items() if not libre]
                if espacios_libres:
                    espacio = random.choice(espacios_libres)
                    espacios[espacio] = True
                    asignacionVehiculos[idVehiculo] = espacio
                    registroEventos.append(f"Carro {idVehiculo} ocupó {espacio}")
                    break
                condicionEspacio.wait(timeout=1.0)

        time.sleep(random.randint(3, 7))

    except Exception as e:
        registroEventos.append(f"Error carro {idVehiculo}: {str(e)}")
    finally:
        vehiculoSalida(idVehiculo)

def vehiculoSalida(idVehiculo):
    """
    libera el espacio asignado a un vehículo y notifica a los hilos en espera

    actualiza el estado de los espacios, libera los permisos del semáforo
    y utiliza notify_all() para despertar a los hilos que esperan por un espacio
    (vehículos esperando lugar)

    Args:
        idVehiculo (int): Identificador del vehículo que está saliendo.
    """
    with condicionEspacio:
        if idVehiculo in asignacionVehiculos:
            espacio = asignacionVehiculos.pop(idVehiculo)
            if isinstance(espacio, tuple):
                for e in espacio:
                    espacios[e] = False
                semaforo.release(2)
                registroEventos.append(f"Carro {idVehiculo} LIBERÓ {espacio[0]} y {espacio[1]}")
            else:
                espacios[espacio] = False
                semaforo.release()
                registroEventos.append(f"Carro {idVehiculo} LIBERÓ {espacio}")
            condicionEspacio.notify_all()

class Grua(threading.Thread):
    """
    hilo encargado de retirar vehículos mal estacionados

    Revisa periódicamente (cada 7 segundos) el estado del estacionamiento y
    retira aquellos vehículos que ocupan dos espacios, liberándolos y notificando
    a los hilos en espera

    """
    def run(self):
        while not stop_event.is_set():
            with mutexEspacios:
                mal_estacionados = [idV for idV, esp in asignacionVehiculos.items() if isinstance(esp, tuple)]
                if mal_estacionados:
                    idV = random.choice(mal_estacionados)
                    espacio1, espacio2 = asignacionVehiculos.pop(idV)
                    espacios[espacio1] = False
                    espacios[espacio2] = False
                    semaforo.release(2)
                    registroEventos.append(f"Grúa RETIRÓ carro {idV} de {espacio1} y {espacio2}")
                    condicionEspacio.notify_all()
            time.sleep(7)

def interfazUsuario():
    """
    actualiza y muestra la interfaz gráfica en tiempo real usando Rich

    presenta una tabla con el estado actual del estacionamiento, incluyendo
    la cantidad de espacios libres, ocupados y los últimos eventos registrados.
    """

    with Live(console=consola, refresh_per_second=4) as live:
        while not stop_event.is_set():
            tabla = Table(
                title="[bold bright_blue]ESTACIONAMIENTO FI PRINCIPAL[/]",
                show_header=True,
                header_style="bold dark_cyan",
                box=None,
                expand=True
            )
            tabla.add_column("Libres", justify="center", style="green", width=15)
            tabla.add_column("Ocupados", justify="center", style="red", width=15)
            tabla.add_column("Eventos Recientes", justify="left", min_width=70)

            with mutexEspacios:
                libres = sum(not estado for estado in espacios.values())
                ocupados = capacidadFisica - libres
                eventos = "\n".join(registroEventos[-10:])
                
            tabla.add_row(
                str(libres),
                str(ocupados),
                eventos
            )
            
            live.update(tabla)
            time.sleep(0.3)

def main():
    """
    función principal que inicia y controla todos los hilos del sistema

    se ejecuta indefinidamente hasta que se interrumpe con Ctrl+C
    donde se controla la finalización de la simulación de manera
    correcta y ordenada
    """
    try:
        Grua(daemon=True).start()
        threading.Thread(target=interfazUsuario, daemon=True).start()
        threading.Thread(target=guardarHistorial, daemon=True).start()
        
        id_counter = 0
        while not stop_event.is_set():
            threading.Thread(target=vehiculoLlegada, args=(id_counter,), daemon=True).start()
            id_counter += 1
            time.sleep(random.uniform(0.4, 1))
    except KeyboardInterrupt:
        stop_event.set()
        print("Deteniendo la simulacion...")
        time.sleep(1)  

if __name__ == "__main__":
    main()
