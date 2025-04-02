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

def guardarHistorial():
    while True:
        with mutexEspacios:
            with open("historial.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(registroEventos[-50:]))
        time.sleep(1)

def ocuparDosEspacios(idVehiculo):
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

        time.sleep(random.randint(2, 5))

    except Exception as e:
        registroEventos.append(f"Error carro {idVehiculo}: {str(e)}")
    finally:
        vehiculoSalida(idVehiculo)

def vehiculoSalida(idVehiculo):
    with condicionEspacio:
        if idVehiculo in asignacionVehiculos:
            espacio = asignacionVehiculos.pop(idVehiculo)
            if isinstance(espacio, tuple):
                for e in espacio:
                    espacios[e] = False
                semaforo.release(2)
            else:
                espacios[espacio] = False
                semaforo.release()
            condicionEspacio.notify_all()

class Grua(threading.Thread):
    def run(self):
        while True:
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
    with Live(console=consola, refresh_per_second=4) as live:
        while True:
            tabla = Table(
                title="[bold bright_blue]ESTACIONAMIENTO FI PRINCIPAL[/]",
                show_header=True,
                header_style="bold dark_cyan",
                box=None,
                expand=True
            )
            
            tabla.add_column("Libres", justify="center", style="green", width=15)
            tabla.add_column("Ocupados", justify="center", style="red", width=15)
            tabla.add_column("Estacionados", justify="center", style="yellow", width=15)
            tabla.add_column("Esperando", justify="center", style="magenta", width=15)
            tabla.add_column("Eventos Recientes", justify="left", min_width=70)

            with mutexEspacios:
                libres = sum(not estado for estado in espacios.values())
                en_espera = sum(1 for e in registroEventos[-20:] if "esperando" in e.lower())
                eventos = "\n".join(registroEventos[-5:])
                
            tabla.add_row(
                str(libres),
                str(capacidadFisica - libres),
                str(len(asignacionVehiculos)),
                str(en_espera),
                eventos
            )
            
            live.update(tabla)
            time.sleep(0.3)

def main():
    Grua(daemon=True).start()
    threading.Thread(target=interfazUsuario, daemon=True).start()
    threading.Thread(target=guardarHistorial, daemon=True).start()
    
    id_counter = 0
    while True:
        try:
            threading.Thread(target=vehiculoLlegada, args=(id_counter,), daemon=True).start()
            id_counter += 1
            time.sleep(random.uniform(0.2, 0.4))
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()