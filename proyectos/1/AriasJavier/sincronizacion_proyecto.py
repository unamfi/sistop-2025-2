import random
import threading
import time

#Variables globales de inicio
trabajos_totales = 0
miembros_totales = 0

#Variables globales
trabajos = []
tareas_pendientes = []
tareas_completadas = []
estado_miembros = {}

# Semaforos y mutex para la sincronización de los hilos
mutex_estado = threading.Semaphore(1)
mutex_tareas_pendientes= threading.Semaphore(1)
mutex_tareas_completadas= threading.Semaphore(1)

semaf_planificador = threading.Semaphore(0)
semaf_tareas = threading.Semaphore(0)

# Asignar los valores dados por el ususario
def initValores(miembros, trabajos):
    global miembros_totales, trabajos_totales

    miembros_totales = miembros
    trabajos_totales = trabajos

# Crear un nuevo ibjeto 'trabajo' que contiene cierto número de tareas
def crearTrabajo(id):

    trabajo = {"id": id, "tareas": []}

    #Determinar el tipo de trabajo
    tipoTrabajo = random.random()

    if tipoTrabajo > 0.5:
        trabajo['tareas'].append(crearTarea(id, 0, 'Planteamiento' ,[]))
        trabajo['tareas'].append(crearTarea(id, 1, 'Análisis' ,[0]))
        trabajo['tareas'].append(crearTarea(id, 2, 'Diseño',[0]))
        trabajo['tareas'].append(crearTarea(id, 3, 'Implementación',[1,2]))
        trabajo['tareas'].append(crearTarea(id, 4, 'Revisión',[3]))
        trabajo['tareas'].append(crearTarea(id, 5, 'Presentación',[3]))

    else:
        trabajo['tareas'].append(crearTarea(id, 0, 'Planteamiento' ,[]))
        trabajo['tareas'].append(crearTarea(id, 1, 'Desarrollo' ,[0]))
        trabajo['tareas'].append(crearTarea(id, 2, 'Conclusión',[1]))
        trabajo['tareas'].append(crearTarea(id, 3, 'Presentación',[1]))

    trabajos.append(trabajo)

#Crear una tarea que se asigna a un trabajo
def crearTarea(id_trabajo, id, nombre, requerimientos):
    tarea = {
        "id_trabajo": id_trabajo,
        "id": id,
        "nombre": nombre,
        "estado": "no empezada",
        "requerimientos": requerimientos,
        "duracion": random.randint(2,5)
    }

    return tarea;

#Planificador que organiza a los distintos miembros del equipo
def planificador():

    #Trabajos en los que se revisará las tareas que se pueden hacer
    trabajos_actualizados = {i for i in range(trabajos_totales)}

    while True:

        # Se revisa que tareas están listas para empezar a realizarse
        for trabajo in trabajos:
            if not trabajo['id'] in trabajos_actualizados:
                continue
            for tarea in trabajo['tareas']:
                if tarea['estado'] == "no empezada" and comprobarTarea(trabajo['tareas'], tarea):

                    #Se agrega la tarea a la lista de tareas pendientes

                    mutex_tareas_pendientes.acquire()
                    tareas_pendientes.append(tarea)
                    tarea['estado'] = "pendiente"
                    mutex_tareas_pendientes.release()

                    # Se le indica a los miembros que hay una tarea lista para realizarse.
                    semaf_tareas.release()

        trabajos_actualizados.clear()

        # Se espera a que se termine una tarea para volver a comprobar los trabajos
        semaf_planificador.acquire()

        #Se revisan las tareas finalizadas para poder revisar los trabajos posteriormente
        mutex_tareas_completadas.acquire()
        while tareas_completadas:
            tarea = tareas_completadas.pop(0)
            trabajos_actualizados.add(tarea['id_trabajo'])
        mutex_tareas_completadas.release()

def miembro(id):
    # Inicializar estado del miembro
    mutex_estado.acquire()
    estado_miembros[id] = None
    mutex_estado.release()

    while True:

        #Se espera a que jaya nuevas tareas listas para ser realizadas
        semaf_tareas.acquire()

        mutex_tareas_pendientes.acquire()
        tarea = tareas_pendientes.pop(0)
        mutex_tareas_pendientes.release()

        # Actualizar estado del miembro
        mutex_estado.acquire()
        estado_miembros[id] = tarea
        mutex_estado.release()

        # Realizando la tarea
        time.sleep(tarea['duracion'])
        tarea['estado'] = "completado"

        # Limpiar estado del miembro
        mutex_estado.acquire()
        estado_miembros[id] = None
        mutex_estado.release()

        # Agregar la tarea a la lista de tareas completadas
        mutex_tareas_completadas.acquire()
        tareas_completadas.append(tarea)
        mutex_tareas_completadas.release()

        semaf_planificador.release()

#Comprobar que se hayan completado todos los requerimientos previos para empezar la tarea
def comprobarTarea(tareas, tarea):
    for requerimiento in tarea['requerimientos']:
        if tareas[requerimiento]['estado'] != "completado":
            return False
    return True
