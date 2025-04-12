/*Autores:
	Nava Benítez David Emilio
	Tavera Castillo David Emmanuel
Proyecto 1
SO		Gpo: 6
*/
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <semaphore.h>
#include <unistd.h>
#include <time.h>


#define IMPRESORAS 4
// Definicion de colores para mejorar la interfaz
#define COLOR_RESET   "\x1b[0m"
#define COLOR_BOLD    "\x1b[1m"
#define COLOR_GREEN   "\x1b[32m"
#define COLOR_YELLOW  "\x1b[33m"
#define COLOR_BLUE    "\x1b[34m"
#define COLOR_RED     "\x1b[31m"

// Variables compartidas y sincronización
sem_t impresora; // Semáforo para controlar el acceso a las impresoras
pthread_mutex_t lock; // Mutex para sincronizar el acceso a variables compartidas
int impresoras_disponibles; // Número de impresoras en funcionamiento
int usuarios_activos; // Número de usuarios en el sistema
int terminar_mantenimiento = 0; // Indicador para finalizar el hilo de mantenimiento
int estado_impresoras[IMPRESORAS]; // Estado de cada impresora (1 = funcional, 0 = descompuesta)
char *nombres_impresoras[IMPRESORAS] = {"Impresora Norte", "Impresora Sur", "Impresora Oriente", "Impresora Poniente"};//nombres de las impresoras
int ultima_impresora_usada = -1; // Última impresora asignada
int impresora_descompuesta = 0; // Indicador de si hay una impresora descompuesta
int en_uso[IMPRESORAS] = {0}; // Indica si una impresora está en uso



void *tarea(void *arg); // Función que simula la tarea de un usuario
int obtenerEntero(char *mensaje, int min, int max);// Función para obtener un número entero dentro de un rango
void *ImpresoraDescompuesta(void *arg);// Función para simular la descomposición de una impresora
int obtenerImpresoraDisponible(); // Función para obtener una impresora disponible
void *RepararImpresora(void *arg);//Función para reparar una impresora dañada
void mostrarMapaImpresoras();//Función para mostra la ubicación de las impresoras
void linea_separadora(); // Función para mostrar una línea separadora en la interfaz

int main() {
    int num_usuarios, num_impresoras, i;
    
    linea_separadora();
    printf(COLOR_BOLD "Sistema de impresoras.\n" COLOR_RESET);
    linea_separadora();
    
    num_usuarios = obtenerEntero("Ingrese el numero de usuarios que van a trabajar el dia de hoy: ", 1, 100);
    num_impresoras = IMPRESORAS;
    impresoras_disponibles = num_impresoras;
    usuarios_activos = num_usuarios;
    for (i = 0; i < IMPRESORAS; i++) estado_impresoras[i] = (i < num_impresoras) ? 1 : 0;
    MapaImpresoras();
    sleep(2);
    pthread_t usuarios[num_usuarios], hilo_mantenimiento;
    pthread_mutex_init(&lock, NULL);
    sem_init(&impresora, 0, num_impresoras);
    srand(time(NULL));
    
    pthread_create(&hilo_mantenimiento, NULL, ImpresoraDescompuesta, NULL);
    pthread_t hilo_reparacion;
	pthread_create(&hilo_reparacion, NULL, RepararImpresora, NULL);
    
    int ids[num_usuarios];
	for (i = 0; i < num_usuarios; i++) {
	    ids[i] = i + 1; 
	}
	// Mezcla aleatoria de los IDs 
	for (i = num_usuarios - 1; i > 0; i--) {
	    int j = rand() % (i + 1);
	    int temp = ids[i];
	    ids[i] = ids[j];
	    ids[j] = temp;
	}
	
    for (i = 0; i < num_usuarios; i++) {
	    int *id = malloc(sizeof(int));
	    *id = ids[i];
	    pthread_create(&usuarios[i], NULL, tarea, id);
	}
    
    for (i = 0; i < num_usuarios; i++) {
        pthread_join(usuarios[i], NULL);
    }
    pthread_join(hilo_mantenimiento, NULL);
	pthread_join(hilo_reparacion, NULL);
    pthread_mutex_destroy(&lock);
    sem_destroy(&impresora);
    return 0;
}

void *tarea(void *arg) {
    int id = *(int *)arg;
    free(arg);
	printf(COLOR_YELLOW "Usuario %d esperando su turno en la sala de espera... \n" COLOR_RESET, id);
    sem_wait(&impresora);
    int impresora_id;
    do {
        impresora_id = obtenerImpresoraDisponible();
        if (impresora_id == -1) {
            usleep(500000); // Esperar medio segundo antes de reintentar
        }
    } while (impresora_id == -1);
    printf(COLOR_BLUE "Usuario %d esta usando %s...\n" COLOR_RESET, id, nombres_impresoras[impresora_id]);
    
    srand(time(NULL) + id);
    int accion = rand() % 3; // Determina qué acción realizará el usuario
    switch (accion) {
        case 0:
            printf(COLOR_BLUE "Usuario %d esta imprimiendo...\n" COLOR_RESET, id);
            sleep(2);
            break;
        case 1:
            printf(COLOR_GREEN "Usuario %d esta sacando copias...\n" COLOR_RESET, id);
            sleep(3);
            break;
        case 2:
            printf(COLOR_RED "Usuario %d esta escaneando...\n" COLOR_RESET, id);
            sleep(4);
            break;
    }

    printf(COLOR_YELLOW "Usuario %d ha terminado su tarea en %s.\n" COLOR_RESET, id, nombres_impresoras[impresora_id]);
    en_uso[impresora_id] = 0;
    sem_post(&impresora);

    pthread_mutex_lock(&lock);
    usuarios_activos--;
    pthread_mutex_unlock(&lock);
    return NULL;
}

int obtenerEntero(char *mensaje, int min, int max) {
    int valor;
    char c;
    while (1) {
        printf(COLOR_BOLD "%s" COLOR_RESET, mensaje);
        if (scanf("%d", &valor) != 1) {
            printf(COLOR_RED "Entrada invalida. Intente nuevamente.\n" COLOR_RESET);
            while ((c = getchar()) != '\n' && c != EOF); // Limpiar buffer
        } else if (valor < min || valor > max) {
            printf(COLOR_RED "Numero fuera de rango. Intente nuevamente.\n" COLOR_RESET);
        } else {
            return valor;
        }
    }
}

void *ImpresoraDescompuesta(void *arg)  {
    sleep(rand() % 5 + 3); // Espera aleatoria antes de descomponer una impresora
    pthread_mutex_lock(&lock);
    if (impresoras_disponibles > 1 && !impresora_descompuesta) {
        int impresora_id;
        do {
            impresora_id = rand() % IMPRESORAS;
        } while (estado_impresoras[impresora_id] == 0 || en_uso[impresora_id] == 1);

        estado_impresoras[impresora_id] = 0;
        impresoras_disponibles--;
        impresora_descompuesta = 1;
        sem_trywait(&impresora);
        printf(COLOR_RED "\n%s se ha descompuesto! Impresoras disponibles: %d\n" COLOR_RESET, nombres_impresoras[impresora_id], impresoras_disponibles);
        MapaImpresoras();
    }
    pthread_mutex_unlock(&lock);
    return NULL;
}

int obtenerImpresoraDisponible() {
    pthread_mutex_lock(&lock);
    int i;
    for ( i = 1; i <= IMPRESORAS; i++) {
        int index = (ultima_impresora_usada + i) % IMPRESORAS;
        if (estado_impresoras[index] == 1 && en_uso[index] == 0) {
            ultima_impresora_usada = index;
            en_uso[index] = 1;
            pthread_mutex_unlock(&lock);
            return index;
        }
    }
    pthread_mutex_unlock(&lock);
    return -1; // No hay impresoras disponibles
}
void *RepararImpresora(void *arg) {
	int i;
    while (usuarios_activos > 0) {
        sleep(10); // Cada cierto tiempo intenta reparar
        pthread_mutex_lock(&lock);
        for(i = 0; i < IMPRESORAS; i++){
            if (estado_impresoras[i] == 0) {
                estado_impresoras[i] = 1;
                impresoras_disponibles++;
                impresora_descompuesta = 0;
                sem_post(&impresora);
                printf(COLOR_GREEN "\n%s ha sido reparada! Impresoras disponibles: %d\n" COLOR_RESET, nombres_impresoras[i], impresoras_disponibles);
                MapaImpresoras();
                break;
            }
        }
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

void MapaImpresoras() {
    printf(COLOR_BOLD "\n\tUbicacion de las impresoras:\n" COLOR_RESET);

    // Impresora Norte 
    printf(COLOR_BLUE "\n\t\t     [NORTE]\n" COLOR_RESET);
    printf("\t\t");
    if (estado_impresoras[0])
        printf(COLOR_GREEN "[OK] %s\n" COLOR_RESET, nombres_impresoras[0]);
    else
        printf(COLOR_RED "[XX] %s\n" COLOR_RESET, nombres_impresoras[0]);

    printf("\n");

    // Impresoras Poniente y Oriente 
    printf(COLOR_YELLOW "\t[PONIENTE]\t\t\t[ORIENTE]\n" COLOR_RESET);

    if (estado_impresoras[3])
        printf(COLOR_GREEN "[OK] %s\t\t", nombres_impresoras[3]);
    else
        printf(COLOR_RED "[XX] %s\t\t", nombres_impresoras[3]);

    if (estado_impresoras[2])
        printf(COLOR_GREEN "[OK] %s\n" COLOR_RESET, nombres_impresoras[2]);
    else
        printf(COLOR_RED "[XX] %s\n" COLOR_RESET, nombres_impresoras[2]);

    printf("\n");

    // Impresora Sur 
    printf(COLOR_BLUE "\t\t     [SUR]\n" COLOR_RESET);
    printf("\t\t");
    if (estado_impresoras[1])
        printf(COLOR_GREEN "[OK] %s\n" COLOR_RESET, nombres_impresoras[1]);
    else
        printf(COLOR_RED "[XX] %s\n" COLOR_RESET, nombres_impresoras[1]);

    linea_separadora();
}

void linea_separadora() {
    printf("\n--------------------------------------------------\n");
}


