//Autor: Meléndez Gómez Anuar       Practica4
#include <stdio.h>

int main() {
    FILE *archivo;

    // Abre el archivo en modo escritura
    archivo = fopen("texto.txt", "w");

    // Verifica si se pudo abrir correctamente
    if (archivo == NULL) {
        printf("Error al crear el archivo.\n");
        return 1;
    }

    // Escribe la frase en el archivo
    fprintf(archivo, "Soy el archivo que debe ser ignorado\n");

    // Cierra el archivo
    fclose(archivo);

    printf("Archivo 'texto.txt' creado correctamente.\n");

    return 0;
}