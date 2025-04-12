import threading
import sys
import time
import curses
from curses import wrapper
from sincronizacion_proyecto import (
    crearTrabajo,
    estado_miembros,
    miembro,
    miembros_totales,
    planificador,
    tareas_pendientes,
    trabajos,
    trabajos_totales,
    initValores
)

evento_cierre = threading.Event()

def actualizar_pantalla(stdscr, trabajos, estado_miembros):
    stdscr.clear()

    # Mostrar título
    stdscr.addstr(1, 1, "SISTEMA DE GESTIÓN DE TAREAS", curses.A_BOLD)

    # Mostrar estado de los trabajos
    stdscr.addstr(3, 1, "ESTADO DE LOS TRABAJOS:", curses.A_UNDERLINE)
    for trabajo in trabajos:
        y = 4 + trabajo['id']
        # Contar tareas completadas
        completadas = sum(1 for tarea in trabajo['tareas'] if tarea['estado'] == "completado")
        total = len(trabajo['tareas'])
        stdscr.addstr(y, 3, f"Trabajo {trabajo['id']}: {completadas}/{total} tareas completadas")

        # Mostrar detalles de las tareas
        for j, tarea in enumerate(trabajo['tareas']):
            estado_symbol = "✓" if tarea['estado'] == "completado" else "⧖" if tarea['estado'] == "pendiente" else "□"
            estado_color = 1 if tarea['estado'] == "completado" else 2 if tarea['estado'] == "pendiente" else 3
            stdscr.addstr(y, 40 + 22 * j, f"{tarea['nombre']}[{estado_symbol}]", curses.color_pair(estado_color))

    # Mostrar estado de los miembros
    y_miembros = 5 + trabajos_totales

    stdscr.addstr(y_miembros, 1, "ESTADO DE LOS MIEMBROS:", curses.A_UNDERLINE)
    for miembro_id, estado in estado_miembros.items():
        y = y_miembros + 1 + miembro_id
        if estado:
            stdscr.addstr(y, 3, f"Miembro {miembro_id}: Trabajando en {estado['nombre']} del Trabajo {estado['id_trabajo']}")
        else:
            stdscr.addstr(y, 3, f"Miembro {miembro_id}: Esperando")

    # Mostrar tareas pendientes
    y_tareas = 7 + trabajos_totales + miembros_totales

    stdscr.addstr(y_tareas, 1, "TAREAS PENDIENTES:", curses.A_UNDERLINE)
    for i, tarea in enumerate(tareas_pendientes):
        stdscr.addstr(y_tareas + 1 + i, 2, f"Tarea {tarea['id']} del Trabajo {tarea['id_trabajo']}")

    stdscr.addstr(stdscr.getmaxyx()[0]-1, 1, "Presione q para salir.")

    stdscr.refresh()

def pantalla_principal(stdscr):
    #Configracion inicial de curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    curses.use_default_colors()

    #Inicialiizacion de los colores
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)

    while not evento_cierre.is_set():
        try:
            actualizar_pantalla(stdscr, trabajos, estado_miembros)
            time.sleep(0.1)

            # Si se presiona 'q', establecer el evento de cierre
            if stdscr.getch() == ord('q'):
                evento_cierre.set()
                break
        except:
            break

def configuracion_inicial():
    while True:
        try:
            miembros = int(input("Ingrese el número de miembros del equipo de trabajo (1-9): "))
            if miembros >= 1 and miembros <= 9:
                break
            print("Valor inválido: Ingrese un número entre 1 y 9.")
        except ValueError:
            print("Valor inválido: Ingrese un número entre 1 y 9.")

    while True:
        try:
            trabajos = int(input("Ingrese el número de trabajos por realizar (1-9): "))
            if trabajos >= 1 and trabajos <= 9:
                break
            print("Valor inválido: Ingrese un número entre 1 y 9.")
        except ValueError:
            print("Valor inválido: Ingrese un número entre 1 y 9.")

    return miembros, trabajos

def main(stdscr):
    global miembros_totales, trabajos_totales

    curses.endwin()
    miembros_totales, trabajos_totales = configuracion_inicial()
    initValores(miembros_totales, trabajos_totales)

    for i in range(trabajos_totales):
        crearTrabajo(i)

    # Iniciar hilos
    threads = []
    for i in range(miembros_totales):
        t = threading.Thread(target=miembro, args=[i])
        t.daemon = True
        t.start()
        threads.append(t)

    t = threading.Thread(target=planificador)
    t.daemon = True
    t.start()
    threads.append(t)

    # Iniciar interfaz
    pantalla_principal(stdscr)

    # Forzar la salida del programa
    sys.exit(0)

if __name__ == '__main__':
    wrapper(main)
