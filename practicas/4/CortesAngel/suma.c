#include <stdio.h>
#include <pthread.h>

#define MENOR 1
#define MAYOR 100
#define NUM 4  // Número de hilos

// Estructura para pasar parámetros a cada hilo
typedef struct {
    int inicio;
    int fin;
    long suma;
} Rango;

void* sumar_rango(void* arg) {
    Rango* rango = (Rango*)arg;
    rango->suma = 0;
    
    // Calcular la suma en el rango específico
    for (int i = rango->inicio; i <= rango->fin; i++) {
        rango->suma += i;
    }

    // Imprimir la suma parcial de este hilo
    printf("Hilo sumando de %d a %d: Suma parcial = %ld\n", rango->inicio, rango->fin, rango->suma);
    
    return NULL;
}

int main() {
    pthread_t hilos[NUM];
    Rango rangos[NUM];
    int intervalo = (MAYOR - MENOR + 1) / NUM;
    long suma_total = 0;

    // Dividir el rango entre los hilos
    for (int i = 0; i < NUM; i++) {
        rangos[i].inicio = MENOR + i * intervalo;
        rangos[i].fin = (i == NUM - 1) ? MAYOR : MENOR + (i + 1) * intervalo - 1;
        
        // Crear los hilos
        pthread_create(&hilos[i], NULL, sumar_rango, &rangos[i]);
    }

    // Esperar que todos los hilos terminen y acumular sus resultados
    for (int i = 0; i < NUM; i++) {
        pthread_join(hilos[i], NULL);
        suma_total += rangos[i].suma;
    }

    // Mostrar la suma total
    printf("La suma total de los números entre %d y %d es: %ld\n", MENOR, MAYOR, suma_total);

    return 0;
}
