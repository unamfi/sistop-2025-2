#include <stdio.h>
#include <omp.h>

int buscaMaximo (int *a, int n) {
    int max,i;
    max=a[0];
    #pragma omp parallel for
        for(i=1;i<n;i++){
            if(a[i]>max) {
                #pragma omp critical
                {
                    if(a[i]>max)
                    max=a[i];
                }
            }
        }

    return max;
}

int main () {
    int n = 6;
    int a[] = {3, 22, 9, 100, 19, 0};
    printf("MAX: %d\n", buscaMaximo(a, n));
    return(0);
}




