#include <omp.h>
#include <stdio.h>

int main (){
  #pragma omp parallel
  {
    printf ("Hola, soy el hilo %d de %d hilos.\n", omp_get_thread_num(), omp_get_num_threads());
  }
}

