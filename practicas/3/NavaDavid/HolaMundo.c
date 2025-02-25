#include <stdio.h>
#define LONGITUD_MAXIMA 50
int main(){
    char nombre[LONGITUD_MAXIMA];
    printf("Nava David - Práctica 3 Segunda Parte\n");
    printf("Ingresa tu nombre: ");
    scanf("%s", nombre);
    printf("Hola, %s",nombre);
    getch();
    return 0;
}
