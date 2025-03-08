package main

import (
	"fmt"
	"math/rand"
	"os"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())
	numero := rand.Intn(100) + 1

	archivo, err := os.Create("numero.txt")
	if err != nil {
		fmt.Println("Error al crear el archivo:", err)
		return
	}
	defer archivo.Close()

	_, err = archivo.WriteString(fmt.Sprintf("Número aleatorio: %d\n", numero))
	if err != nil {
		fmt.Println("Error al escribir en el archivo:", err)
		return
	}

	fmt.Println("Archivo 'numero.txt' creado con éxito.")
}
