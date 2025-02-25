#include<stdio.h>
int main(){
    printf("Dame tu nombre por favor: \n");
    char nombre[100];
    scanf("%[^\n]", nombre);
    printf("Hola %s\n", nombre);
    return 0;
}