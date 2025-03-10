#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

typedef struct {
    unsigned long long fib_n;
    time_t init_time;
} thread_args;

// Recursive fibonacci function
unsigned long long fib(unsigned long long n) {
    if (n == 0) return 1;
    if (n == 1) return 1;
    return fib(n - 1) + fib(n - 2);
}

void *thread_function(void *arg) {
    thread_args *targ = (thread_args *) arg;

    time_t init_time = time(NULL) - targ->init_time;

    unsigned long long n = targ->fib_n;
    unsigned long long res = fib(n);

    printf("Thread #%ld started at %ld, finished at %ld, the result is %llu\n", n, init_time, time(NULL) - targ->init_time, res);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <number of threads>\n", argv[0]);
        return 1;
    }

    int thread_num = atoi(argv[1]);

    time_t init_time = time(NULL);

    pthread_t threads[thread_num];
    for (unsigned long long i = 0; i < thread_num; i++) {
        thread_args *arg = (thread_args *) malloc(sizeof(thread_args));
        arg->fib_n = i;
        arg->init_time = init_time;
        pthread_create(&threads[i], NULL, thread_function, arg);
    }

    for (int i = 0; i < thread_num; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Final time: %ld\n", time(NULL) - init_time);
    return 0;
}