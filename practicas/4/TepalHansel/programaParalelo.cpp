#include <iostream>
#include <vector>
#include <thread>
#include <algorithm>
#include <chrono>

void merge(std::vector<int>& arr, int left, int right, int mid){
    int n1 = mid - left + 1;
    int n2 = right - mid;
    std::vector<int> L(n1), R(n2);

    for(int i = 0; i < n1; i++){
        L[i] = arr[left + i];
    }
    for(int i = 0; i < n2; i++){
        R[i] = arr[mid + 1 + i];
    }

    int i = 0, j = 0, k = left;
    while(i < n1 && j < n2){
        if(L[i] <= R[j]){
            arr[k] = L[i];
            i++;
        }else{
            arr[k] = R[j];
            j++;
        }
        k++;
    }
    while(i < n1){
        arr[k] = L[i];
        i++;
        k++;
    }
    while(j < n2){
        arr[k] = R[j];
        j++;
        k++;
    }
}

void merge_sort_iterative(std::vector<int>& arr){
    int n = arr.size();
    for(int size = 1; size < n; size = 2 * size){
        for(int left = 0; left < n - size; left += 2 * size){
            int mid = std::min(left + size - 1, n - 1);
            int right = std::min(left + 2 * size - 1, n - 1);
            merge(arr, left, right, mid);
        }
    }
}

void merge_sort_parallel(std::vector<int>& arr, int left, int right){
    if(left < right){
        int mid = left + (right - left) / 2;
        
        std::thread t1(merge_sort_parallel, std::ref(arr),left, mid);
        std::thread t2(merge_sort_parallel, std::ref(arr), mid + 1, right);

        t1.join();
        t2.join();

        merge(arr, left, right, mid);
    }
}

int main(){
    std::vector<int> arr = {64, 34, 25, 12, 22, 11, 90, 3, 7, 56, 89, 1, 2, 6, 30, 13, 45, 66, 11, 10};

    // Comparar Merge Sort Iterativo vs Paralelo

    std::vector<int> arr_iterative = arr;  // Copia del arreglo para el caso iterativo
    std::vector<int> arr_parallel = arr;   // Copia del arreglo para el caso paralelo

    // Tiempo de ejecución del Merge Sort Iterativo
    auto start_iterative = std::chrono::high_resolution_clock::now();
    merge_sort_iterative(arr_iterative);
    auto end_iterative = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration_iterative = end_iterative - start_iterative;

    // Tiempo de ejecución del Merge Sort Paralelo
    auto start_parallel = std::chrono::high_resolution_clock::now();
    merge_sort_parallel(arr_parallel, 0, arr_parallel.size() - 1);
    auto end_parallel = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> duration_parallel = end_parallel - start_parallel;

    // Imprimir resultados
    std::cout << "Array original: " << std::endl;
    for(int i = 0; i < arr.size(); i++){
        std::cout << arr[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Array ordenado por Merge Sort Iterativo: " << std::endl;
    for(int i = 0; i < arr_iterative.size(); i++){
        std::cout << arr_iterative[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Array ordenado por Merge Sort Paralelo: " << std::endl;
    for(int i = 0; i < arr_parallel.size(); i++){
        std::cout << arr_parallel[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Tiempo de ejecución de Merge Sort Iterativo: " << duration_iterative.count() << " segundos." << std::endl;
    std::cout << "Tiempo de ejecución de Merge Sort Paralelo: " << duration_parallel.count() << " segundos." << std::endl;

    return 0;
}
