#Este es un programa que obtiene el nombre de un usuario desde la linea de comando"

def main():
    # Solicita al usuario que ingrese su nombre
    nombre = input("Por favor, ingresa tu nombre: ")
    
    # Muestra un saludo personalizado
    print(f"¡Hola, {nombre}! Bienvenido/a.")

if __name__ == "__main__":
    main()