#include<stdio.h>
#include<omp.h>

static long num_steps=10000;

double step;
//Integral de 4/(1+x²);
int main()
{
    double pi,sum=0.0;
    step=1.0/(double)num_steps;
    int max=omp_get_max_threads();
    double arr[max];
    for(int i=0;i<max;i++)
    {
        arr[i]=0.0;
    }
    omp_set_num_threads(max);
    #pragma omp parallel 
    {
        int id=omp_get_thread_num();
        double x=0.0;
        for(int i=id;i<num_steps;i+=max)
        {
            x=(i+0.5)*step;
            arr[id]=arr[id]+4.0/(1.0+x*x);
        }
    }
    for(int i=0;i<max;i++)
    {
        sum+=arr[i];
    }
    pi=step*sum;
    printf("Sum=%f\n",pi);
    return 0;
}