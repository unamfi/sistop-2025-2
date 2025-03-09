#include <stdio.h>
#include <omp.h>

int main() {
    printf("Program that greets you from each thread of your computer :b\n");

    int num_threads = omp_get_num_procs();

    omp_set_num_threads(num_threads);

    #pragma omp parallel
    {
        int thread_id = omp_get_thread_num();
        printf("Hello, this is thread number %d/n", thread_id);
    }

    return 0;
}
