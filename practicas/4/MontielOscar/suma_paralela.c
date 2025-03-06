
#include <stdio.h>
#include <omp.h>

#define N 1000

int main() {
    int array[N];
    int suma = 0;

    
    for (int i = 0; i < N; i++) {
        array[i] = i + 1;
    }

    #pragma omp parallel for reduction(+:suma)
    for (int i = 0; i < N; i++) {
        suma += array[i];
    }

    printf("La suma de los elementos del arreglo es: %d\n", suma);

    return 0;
}
