import pygame
import threading as thr
import time
import random
import sys


# Inicialización de Pygame
pygame.init()
WIDTH, HEIGHT = 650, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Roomies")
font = pygame.font.SysFont("Arial", 24)
log_font = pygame.font.SysFont("Courier New", 18)
clock = pygame.time.Clock()

#Diccionarios de estados para los cuadros de tareas y roomies
estado_tareas = {
    'Lavar los trastes': 'inactiva',
    'Barrer': 'inactiva',
    'Trapear': 'inactiva',
    'Sacar la basura': 'inactiva',
    'Comprar Fruta': 'inactiva',
    'Llenar el garrafon' : 'inactiva'
}
estado_roomies = {
    'Jesus': 'despierto',
    'Carlos': 'despierto'
}

logs = []  # Historial de eventos

# Variables compartidas
mutex_tareas = thr.Semaphore(2)
semf_trapear = thr.Semaphore(0)
semf_dia = thr.Semaphore(0)

#Variables para el rendezvous
rendJ = thr.Semaphore(0)
rendC = thr.Semaphore(0)

#Globales
cubiertos = True
stack_tareas = []
dias = 0
esperando_avance = True
fin_simulacion = False

def add_log(msg):                   
    wrapped = wrap_text(msg, log_font, WIDTH - 80)  # Guarda los mensajes de la ejecución en un arreglo para mostrar en pantalla. 
    logs.extend(wrapped)                            #Incluye un método para ajustar el texto en pamtalla
    max_lines = (HEIGHT - 260) // 20
    if len(logs) > max_lines:
        logs[:] = logs[-max_lines:]

def wrap_text(text, font, max_width):               #Esto es lo que ajusta el texto
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + ' '
    if current_line:
        lines.append(current_line.strip())
    return lines

# ========== Lógica de tareas y roomies ========== #
def set_tareas():
    global dias
    logs.clear()     #Limpia los logs en pantalla para facilitar la lectura

    stack_tareas.append('Trapear')
    estado_tareas['Trapear'] = 'pendiente'                  #El orden 'por defecto' de las tareas es también el orden para los días 4 y 5
    stack_tareas.append('Sacar la basura')
    estado_tareas['Sacar la basura'] = 'pendiente'
    stack_tareas.append('Barrer')
    estado_tareas['Barrer'] = 'pendiente'
    stack_tareas.append('Lavar los trastes')
    estado_tareas['Lavar los trastes'] = 'pendiente'
    
    if dias == 0:                                           #En Lunes, se elimina el lavado de trastes inicial
        stack_tareas.pop()
        estado_tareas['Lavar los trastes'] = 'inactiva'
            
    if dias == 1:                                       #Martes se aprovechan los martes de frescura
        stack_tareas.append('Comprar Fruta')
        estado_tareas['Comprar Fruta'] = 'pendiente'
    else: 
        estado_tareas['Comprar Fruta'] = 'inactiva'
    
    if dias == 2:                                       #Los miércoles se va a la purificadora de agua
        stack_tareas.append('Llenar el garrafon')
        estado_tareas['Llenar el garrafon'] = 'pendiente'
    else: 
        estado_tareas['Llenar el garrafon'] = 'inactiva'
    
    if dias < 3:
        random.shuffle(stack_tareas)            
        
    add_log(f"=== Día {dias + 1} ===")
    add_log(f"Tareas asignadas: {stack_tareas}")


def hacer_tarea(tarea, roomie):
    add_log(f"[{roomie}] haciendo: {tarea}")
    
    match tarea:
        case 'Lavar los trastes' | 'Lavar los cubiertos':       #Para fines prácticos, cubiertos y trastes dan a la misma actividad
            time.sleep(0.5)                                     #solo cambia el nombre
        case 'Barrer':
            semf_trapear.release()
            time.sleep(0.5)
        case 'Trapear':
            semf_trapear.acquire()
            time.sleep(0.7)
        case 'Sacar la basura':
            time.sleep(0.3)
        case 'Comprar Fruta':
            time.sleep(1)
        case 'Llenar el garrafon':
            time.sleep(1)
    if tarea=='Lavar los cubiertos':
        estado_tareas['Lavar los trastes'] = 'completada'
    else:
        estado_tareas[tarea] = 'completada'


def comer(nombre):
    global cubiertos
    add_log(f"[{nombre}] quiere comer")
    
    while True:
        if cubiertos:
            add_log(f"[{nombre}] Comiendo... Ñam Ñam")
            time.sleep(1)
            
            if random.randint(1, 2) == 2 or dias >= 4:                  #50% de probailidad de lavar cubiertos, o asegurado para los días 4 y 5
                add_log(f"[{nombre}] Lavando los cubiertos que usó")
                time.sleep(0.5)
            else:
                add_log(f"[{nombre}] Dejó los cubiertos sucios :/ ")
                estado_tareas['Lavar los trastes'] = 'pendiente'
                stack_tareas.append('Lavar los cubiertos')
                cubiertos = False
                
            estado_tareas['Lavar los trastes'] = 'pendiente'
            stack_tareas.append('Lavar los trastes')
            break
        
        else:
            add_log(f"[{nombre}] está lavando los cubiertos antes de comer")
            cubiertos = True


def roomieJ(nombre):
    global dias, esperando_avance
    while dias <= 4:
        Hambre = True
        estado_roomies[nombre] = 'despierto'
        
        with mutex_tareas:
            while stack_tareas:
                hacer_tarea(stack_tareas.pop(), nombre)
                if Hambre and random.randint(1, 3) == 2:
                    comer(nombre)
                    Hambre = False
            if Hambre:
                comer(nombre)
                
        add_log(f"[{nombre}] terminó sus tareas del día")
        estado_roomies[nombre] = 'dormido'

        if dias < 3:
            semf_dia.acquire()
        
        if dias != 4:                                                           
            add_log(">> Presiona ESPACIO para avanzar al siguiente día")
        else:                                                #Cambia la instrucción al 5to día                                                                                                                                                                                                                                                                                                                   
            add_log("¡Terminamos la semana!")                                                                                                                                                                                                                                                                                                                                                                                                                                               
            add_log(">>>Presiona ENTER para cerrar.")
            global fin_simulacion
            fin_simulacion = True
            break
            
        while esperando_avance:
            time.sleep(0.1)
        esperando_avance = True
        
        dias += 1
        
        if dias < 4:                    #En toría debería ser <3, pero se hace el aumento de días antes de esto, y si lo cambio
            rendC.release()             #el programa deja de funcionar, no se muy bien por qué
            rendJ.acquire()
        set_tareas()
        

def roomieC(nombre):
    global dias
    
    while dias < 3:                                 #No tiene caso que su ciclo dure 5 días
        estado_roomies[nombre] = 'despierto'
        Hambre = True
        with mutex_tareas:
            while stack_tareas:
                hacer_tarea(stack_tareas.pop(), nombre)
                if Hambre and random.randint(1, 5) < 5:
                    comer(nombre)
                    Hambre = False
            if Hambre:
                comer(nombre)
                
        add_log(f"[{nombre}] terminó sus tareas del día")
        estado_roomies[nombre] = 'dormido'
        semf_dia.release()
        rendJ.release()
        rendC.acquire()
    add_log("=== Carlos se va al rancho ===")
    estado_roomies[nombre] = 'fuera'

# ========== Visualización con Pygame ==========
def draw():
    screen.fill((0, 0, 0))
    semana = ['Lunes','Martes','Miercoles','Jueves','Viernes']      #Lista de días de la semana, para no mostrar sólo el numero de día
    title = font.render(f"Hoy es {semana[dias]}", True, (255, 255, 0), (0,0,0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
    
    # Mostrar logs
    y = 70
    for log in logs:
        log_surface = log_font.render(log, True, (255, 255, 255))
        screen.blit(log_surface, (50, y-20))
        y += 20
        
    # Dibujar las tareas
    tarea_nombres = list(estado_tareas.keys())
    box_size = 40
    spacing = 60
    start_x = 50
    start_y = HEIGHT - 120

    for i, tarea in enumerate(tarea_nombres):
        estado = estado_tareas[tarea]
        color = {
            'pendiente': (255, 0, 0),
            'completada': (0, 200, 0),
            'inactiva': (160, 160, 160)
        }[estado]

        x = start_x + i * (box_size + spacing)
        pygame.draw.rect(screen, color, (x, start_y, box_size, box_size))
        text_surface = log_font.render(tarea.split()[0], True, (255, 255, 255))
        screen.blit(text_surface, (x, start_y + box_size + 5))

    # Dibujar roomies
    roomie_pos = {'Jesus': 200, 'Carlos': 400}
    for nombre, estado in estado_roomies.items():
        color = {
            'despierto': (60, 236, 247),
            'dormido': (148, 63, 228),
            'fuera': (128, 128, 128)
        }[estado]

        pygame.draw.rect(screen, color, (roomie_pos[nombre], HEIGHT - 200, 40, 40))
        label = log_font.render(nombre[0], True, (0, 0, 0))
        screen.blit(label, (roomie_pos[nombre] + 10, HEIGHT - 190))

    pygame.display.flip()


# ========= Pantalla de inicio ==========
esperando_inicio = True
while esperando_inicio:
    screen.fill((0, 0, 0))
    title = font.render("Simulación de Roomies", True, (255, 255, 0))
    prompt = log_font.render("Presiona ENTER para comenzar", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            esperando_inicio = False

# ========= Cuenta regresiva ==========
for i in range(3, 0, -1):
    screen.fill((0, 0, 0))
    title = font.render("Simulación de Roomies", True, (255, 255, 0))
    countdown = log_font.render(f"Comenzando en {i}...", True, (255, 255, 255))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 60))
    screen.blit(countdown, (WIDTH // 2 - countdown.get_width() // 2, HEIGHT // 2))
    pygame.display.flip()
    time.sleep(1)

# ========== Hilo principal ==========
set_tareas()
t1 = thr.Thread(target=roomieJ, args=["Jesus"])
t2 = thr.Thread(target=roomieC, args=["Carlos"])
t1.start()
t2.start()

# Loop de Pygame
running = True
while running:
    draw()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if fin_simulacion and event.key == pygame.K_RETURN:
                running = False
            elif esperando_avance and event.key == pygame.K_SPACE and not fin_simulacion:
                esperando_avance = False           
    clock.tick(30)

pygame.quit()

t1.join()                   #Los hilos se crearon como variables para poder usar .join()
t2.join()                   #Sin esto, la ventana se cierra al terminar el juego, pero la terminal se
sys.exit()                  #congela

