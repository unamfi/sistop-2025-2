#include <stdio.h>
#include <omp.h>

int main()
{

#ifdef _OPENMP
    printf("OpenMP está activo con %d hilos disponibles.\n", omp_get_max_threads());
#endif

#pragma omp parallel num_threads(3)
    {
        int id = omp_get_thread_num();
        printf("Hola desde el hilo %d\n", id);
    }

    printf("Todos los hilos han terminado.\n");

    return 0;
}
