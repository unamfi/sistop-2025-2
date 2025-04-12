import pygame
import random
import threading
from Cliente import *
from Champion import Champion
from Platos import *
def inicio(pantalla, fuente, ANCHO, ALTO):
    # Cargar fondo
    fondo = pygame.image.load("assets/fondoChamps.png")  
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    NUM_CLIENTES = 10
    NUM_PLATOS = 3
    NUM_SLOTS = 10
    CUADRO = 180
    ZONA_H = 200
    ZONA_Y = ALTO - ZONA_H
    ZONA_W = ANCHO

    # Crear lock y slots compartidos
    lock = threading.Lock()
    slots = [None] * NUM_SLOTS

    # Crear champion y platos
    champion = Champion()
    platos = Platos(NUM_PLATOS)

    # Crear e iniciar hilos de clientes
    clientes = [Cliente(i, champion, platos) for i in range(NUM_CLIENTES)]
    for c in clientes:
        c.nombre = "Cliente_" + str(random.randint(1, 100))  # Nombre random
        c.lock = lock
        c.slots = slots
        c.start()

    corriendo = True
    # Ciclo principal
    while corriendo:
        # Ajustamos el fondo
        pantalla.blit(fondo, (0, 0))

        # Revisamos si se intenta salir del programa
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        # HUD visual de todos los clientes (esperando, comiendo, apagados)
        with lock:
            clientes_en_slots = set(slots)  # Para verificar fácilmente si ya está siendo renderizado

       # Ajustar la posición de los clientes fuera de los slots (más abajo pero con menos traslape)
        for i, cliente in enumerate(clientes):
            if cliente.estado == "apagado":
                continue  # No renderizar clientes apagados

            if cliente in clientes_en_slots:
                continue  # Ya está siendo renderizado en la zona de slots

            # Para renderizar los clientes más abajo, ajustamos la coordenada y
            x = 30 + (i % 5) * (CUADRO + 10)
            y = ALTO - 200 + (i % 2) * 50  # Reducimos el traslape al ajustar la altura ligeramente

            # Mostrar el estado del cliente encima de su imagen
            estado_texto = fuente.render(f"{cliente.estado.capitalize()}", True, (255, 255, 255))
            pantalla.blit(estado_texto, (x+30, y - 5))  # Aquí mostramos el estado por encima

            # Renderizamos la imagen del cliente
            pantalla.blit(cliente.image, (x, y))

        # Visualización adicional de los clientes en la zona reservada (slots)
        with lock:
            for i, cliente in enumerate(slots):
                if cliente:
                    slot_width = ZONA_W // NUM_SLOTS
                    x = i * slot_width + (slot_width - CUADRO) // 2
                    y = ZONA_Y + ZONA_H - CUADRO + 30 - 30  # Moverlos un poco más arriba

                    # Mostrar el estado del cliente en la zona reservada (slots)
                    estado_texto = fuente.render(f"{cliente.estado.capitalize()}", True, (255, 255, 255))
                    pantalla.blit(estado_texto, (x+30, y - 5))  # Mostrar el estado encima de la imagen

                    pantalla.blit(cliente.image, (x, y))


                    
        # Calculamos elementos del HUD
        comiendo = sum(1 for cliente in slots if cliente is not None)
        activos = sum(1 for cliente in clientes if cliente.estado != "apagado")
        apagados = sum(1 for cliente in clientes if cliente.estado == "apagado")
        platos_disponibles = platos.semaforo._value  # Accedemos al valor del semáforo
        
        # Los textos ahora se renderizan en la esquina superior izquierda
        texto_comiendo = fuente.render(f"Clientes comiendo: {comiendo} / {NUM_PLATOS}", True, (255, 255, 255))
        texto_activos = fuente.render(f"Clientes activos: {activos} / {NUM_CLIENTES}", True, (255, 255, 255))
        texto_apagados = fuente.render(f"Clientes apagados: {apagados}", True, (255, 255, 255))
        texto_platos = fuente.render(f"Platos disponibles: {platos_disponibles} / {NUM_PLATOS}", True, (255, 255, 255))

        # Renderizamos los textos en la parte superior izquierda
        pantalla.blit(texto_comiendo, (10, 10))
        pantalla.blit(texto_activos, (10, 40))
        pantalla.blit(texto_apagados, (10, 70))
        pantalla.blit(texto_platos, (10, 100))
        
        """Información del Champion para el HUD"""
        # Obtener el estado actual del champion
        estado_champion = champion.estado

        # Renderizar el estado del champion
        estado_champion_texto = fuente.render(f"Estado Champion: {estado_champion}", True, (255, 255, 255))

        # Posicionar el estado del champion en la esquina superior derecha
        pantalla.blit(estado_champion_texto, (ANCHO - estado_champion_texto.get_width() - 10, 10))
        pygame.display.flip()
        clock.tick(60)
        if(apagados == NUM_CLIENTES):
            champion.estado = "Inactivo"

    print("FIN.")
