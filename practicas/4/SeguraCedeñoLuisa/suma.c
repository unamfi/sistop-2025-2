#include <stdio.h>

int main() {
    FILE *archivo;

    // Abrimos el archivo en modo escritura
    archivo = fopen("salida.txt", "w");

    // Verificamos si se pudo abrir correctamente
    if (archivo == NULL) {
        printf("Error al crear el archivo.\n");
        return 1;
    }

    // Escribimos en el archivo
    fprintf(archivo, "Este es un archivo generado por el programa en C.\n");

    // Cerramos el archivo
    fclose(archivo);

    printf("Archivo 'salida.txt' generado con éxito.\n");

    return 0;
}

