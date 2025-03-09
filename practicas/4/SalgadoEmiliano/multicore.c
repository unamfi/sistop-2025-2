#include <stdio.h>
#include <stdlib.h>
#include <omp.h>

int main()
{
    #pragma omp parallel
    {
        printf("Hello world!\n");
        for (int i = 0; i <10 ; i++){
            printf("Iteracion: %d\n", i);
        }
        printf("Adios\n");
    } //TERMINA REGION PARALELA
    return 0;
}
