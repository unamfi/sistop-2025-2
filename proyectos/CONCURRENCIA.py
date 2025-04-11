import threading
import time
import random
from rich.console import Console
from rich.text import Text
from rich.panel import Panel

# Recursos compartidos: semáforos
semaforo_bano = threading.Semaphore(1)  # Solo una persona en el baño
semaforo_lavabo = threading.Semaphore(1)  # Solo una persona usando el lavabo
semaforo_regadera = threading.Semaphore(1)  # Solo una persona bañándose
semaforo_inodoro = threading.Semaphore(1)  # Solo una persona en el inodoro

# Personas
personas = ["Francisco", "Lorena", "Jair", "Itzel", "Barvara"]

# Estado de cada persona
estado_personas = {nombre: {"banado": False} for nombre in personas}

# Consola Rich
console = Console()

def escribir_log(mensaje, color="white"):
    console.print(Text(mensaje, style=color))

def hacer_del_bano(nombre):
    escribir_log(f"{nombre} quiere hacer del baño.", "cyan")
    with semaforo_bano:
        escribir_log(f"{nombre} entra al baño.", "yellow")
        with semaforo_inodoro:
            escribir_log(f"{nombre} está haciendo del baño.", "magenta")
            time.sleep(random.uniform(1, 3))
            escribir_log(f"{nombre} terminó en el baño.", "magenta")
        escribir_log(f"{nombre} sale del baño.", "yellow")

def banarse(nombre):
    if estado_personas[nombre]["banado"]:
        escribir_log(f"{nombre} ya se ha bañado antes, no se bañará otra vez.", "red")
        return

    escribir_log(f"{nombre} quiere bañarse.", "cyan")
    with semaforo_bano:
        escribir_log(f"{nombre} entra al baño.", "yellow")
        with semaforo_regadera:
            escribir_log(f"{nombre} se está bañando.", "blue")
            time.sleep(random.uniform(2, 4))
            escribir_log(f"{nombre} terminó de bañarse.", "blue")
            estado_personas[nombre]["banado"] = True
        escribir_log(f"{nombre} sale del baño.", "yellow")

def cepillarse(nombre):
    escribir_log(f"{nombre} quiere cepillarse los dientes.", "cyan")
    with semaforo_bano:
        escribir_log(f"{nombre} entra al baño.", "yellow")
        with semaforo_lavabo:
            escribir_log(f"{nombre} se está cepillando los dientes.", "green")
            time.sleep(random.uniform(1, 3))
            escribir_log(f"{nombre} terminó de cepillarse.", "green")
        escribir_log(f"{nombre} sale del baño.", "yellow")

def persona_actua(nombre):
    acciones = [hacer_del_bano, banarse, cepillarse]
    prioridades = {
        hacer_del_bano: 1,
        banarse: 2,
        cepillarse: 2
    }
    for _ in range(4):
        acciones_disponibles = sorted(acciones, key=lambda x: prioridades[x])
        accion = random.choice(acciones_disponibles)
        accion(nombre)
        time.sleep(random.uniform(0.5, 1.5))

def main():
    console.print(Panel("[bold]Simulación de uso del baño[/bold]", style="bold green"))
    hilos = []
    for persona in personas:
        t = threading.Thread(target=persona_actua, args=(persona,))
        hilos.append(t)
        t.start()

    for t in hilos:
        t.join()

    console.print(Panel("[bold green]\nSimulación terminada.[/bold green]"))

if __name__ == "__main__":
    main()
