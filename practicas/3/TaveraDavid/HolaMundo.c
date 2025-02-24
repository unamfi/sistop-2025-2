#include <stdio.h>

int main(void) {
    char nombre[50]; 
    printf("Ingresa tu nombre: ");
    scanf("%49s", nombre);
    printf("Hola, %s\n", nombre);
    return 0;
}

