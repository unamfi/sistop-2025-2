#include <stdio.h>
#include <omp.h>
//Programa que busca el numero mas grande dentro de un arreglo
int ordenaM (int *a, int n) { //Se envia el arreglo y el numero de datos que debe analizar
    int grand,i;
    grand=a[0];
    #pragma omp parallel for
        for(i=1;i<n;i++){
            if(a[i]>grand) {
                #pragma omp critical
                {
                    if(a[i]>grand)
                    grand=a[i];
                }
            }
        }

    return grand;
}

int main () {
    int n = 10;
    int a[] = {3, 22, 9, 100, 19, 0,11000,15632,201932,2012010};
    printf("Bienvenido usuario\n");
    printf("Tu numero mas grande es: %d\n", ordenaM(a, n));
    return(0);
}
