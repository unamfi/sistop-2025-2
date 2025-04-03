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

//Semaforo para controlar el acceso a una impresora
sem_t impresora;
pthread_mutex_t lock;
int impresoras_disponibles;
int usuarios_activos;
int terminar_mantenimiento = 0;


void *tarea(void *arg);
int obtenerEntero(char *mensaje, int min, int max);
void *ImpresoraDescompuesta(void *arg);
void linea_separadora();

int main() {
    int num_usuarios, num_impresoras, i;
    
    linea_separadora();
    printf(COLOR_BOLD "Sistema de impresoras.\n" COLOR_RESET);
    linea_separadora();
    
    num_usuarios = obtenerEntero("Ingrese el numero de usuarios: ", 1, 100);
    num_impresoras = obtenerEntero("Ingrese el numero total de impresoras (max 4): ", 1, IMPRESORAS);
    impresoras_disponibles = num_impresoras;
    usuarios_activos = num_usuarios;
    
    pthread_t usuarios[num_usuarios], hilo_mantenimiento;
    pthread_mutex_init(&lock, NULL);
    sem_init(&impresora, 0, num_impresoras);
    srand(time(NULL));
    
    pthread_create(&hilo_mantenimiento, NULL, ImpresoraDescompuesta, NULL);
    
    printf(COLOR_GREEN "\nIniciando tareas de los usuarios...\n" COLOR_RESET);
    linea_separadora();
    
    for (i = 0; i < num_usuarios; i++) {
        int *id = malloc(sizeof(int));
        *id = i + 1;
        pthread_create(&usuarios[i], NULL, tarea, id);
        usleep(100000);  // Pausa corta entre creaciones de hilos
    }
    
    for (i = 0; i < num_usuarios; i++) {
        pthread_join(usuarios[i], NULL);
    }
    
    pthread_mutex_lock(&lock);
    terminar_mantenimiento = 1;
    pthread_mutex_unlock(&lock);
    
    pthread_join(hilo_mantenimiento, NULL);
    pthread_mutex_destroy(&lock);
    sem_destroy(&impresora);
    
    linea_separadora();
    printf(COLOR_GREEN "El sistema ha finalizado todas las tareas.\n" COLOR_RESET);
    linea_separadora();
    
    return 0;
}


void *tarea(void *arg) {
    int id = *(int *)arg;
    free(arg);

    printf(COLOR_YELLOW "Usuario %d esperando su turno...\n" COLOR_RESET, id);
    sem_wait(&impresora);

    pthread_mutex_lock(&lock);
    if (impresoras_disponibles == 0) {
        pthread_mutex_unlock(&lock);
        printf(COLOR_RED "Usuario %d reubicado debido a una impresora descompuesta.\n" COLOR_RESET, id);
        sem_wait(&impresora);
    } else {
        pthread_mutex_unlock(&lock);
    }

    unsigned int seed = time(NULL) + id * 31; 
    srand(seed);
    int accion = rand() % 3;
    
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
    
    printf(COLOR_YELLOW "Usuario %d ha terminado su tarea.\n" COLOR_RESET, id);
    sem_post(&impresora);

    pthread_mutex_lock(&lock);
    usuarios_activos--;
    pthread_mutex_unlock(&lock);
    
    return NULL;
}

//validación de entradas 
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
//Función para emular cuando una impresora se descompone.
void *ImpresoraDescompuesta(void *arg) {
    while (1) {
        sleep(1); 
        
        pthread_mutex_lock(&lock);
        if (terminar_mantenimiento) {
            pthread_mutex_unlock(&lock);
            break;
        }
        pthread_mutex_unlock(&lock);
        
        int espera = rand() % 6 + 5,i; // Tiempo entre 5 y 10 segundos
        for ( i = 0; i < espera; i++) {
            sleep(1);
            pthread_mutex_lock(&lock);
            if (terminar_mantenimiento) {
                pthread_mutex_unlock(&lock);
                return NULL;
            }
            pthread_mutex_unlock(&lock);
        }
        
        pthread_mutex_lock(&lock);
        if (impresoras_disponibles > 1 && usuarios_activos > 0) {
            impresoras_disponibles--;
            sem_trywait(&impresora);  // Reducir disponibilidad sin bloquear
            printf(COLOR_RED "\nUna impresora se ha descompuesto! Impresoras disponibles: %d\n" COLOR_RESET, impresoras_disponibles);
        }
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

void linea_separadora() {
    printf("\n--------------------------------------------------\n");
}


