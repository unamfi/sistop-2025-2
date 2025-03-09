#include <stdio.h>
#include <pthread.h>

void* imprimir_numeros(void* arg) {
    for(int i = 1; i <= 5; i++) {
        printf("Número: %d\n", i);
    }
    return NULL;
}

int main() {
    pthread_t hilo;  

    pthread_create(&hilo, NULL, imprimir_numeros, NULL);
    printf("Mensaje que se ejecuta mientras el hilo trabaja.\n");
    pthread_join(hilo, NULL);
    printf("Fin del hilo.\n");

    return 0;
}
