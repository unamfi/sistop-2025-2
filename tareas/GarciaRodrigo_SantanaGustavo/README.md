## **Problema que se decidió resolver** 
Este programa simula el **problema de sincronización de Santa Claus**, en el que Santa está dormido hasta que ciertos eventos lo despiertan:  
- **Si llegan 9 renos de sus vacaciones**, Santa se despierta para preparar su trineo.  
- **Si hay 3 elfos esperando ayuda**, Santa se despierta para atenderlos.  

El objetivo es sincronizar estos eventos correctamente, garantizando que Santa solo despierte cuando sea necesario.  

## **Lenguaje y entorno**  
El programa está desarrollado en Java utilizando el paquete `java.util.concurrent` para manejar la sincronización entre hilos. Se ejecuta en cualquier entorno con Java instalado (JDK 8 o superior).  

## Requisitos para ejecutar el programa  
Para ejecutar el programa en tu computadora, necesitas:  
1. Java Development Kit (JDK) 8 o superior instalado.  
2. Un compilador de Java (como `javac`).  
3. Una terminal o consola para compilar y ejecutar el código.  

### Pasos para ejecutar  
1. Guarda el archivo con el nombre `Main.java`.  
2. Abre una terminal en la misma ubicación del archivo.  
3. Compila el programa con:  
   ```
   javac Main.java
   ```  
4. Ejecuta el programa con:  
   ```
   java Main
   ```  
5. Ingresa el número de elfos cuando se solicite.  

## Estrategia de sincronización  
El programa usa los siguientes mecanismos de sincronización:  
- *Semáforo (`Semaphore`)*: Controla cuántos elfos pueden esperar ayuda a la vez (máximo 3).  
- *CyclicBarrier*: Sincroniza a los elfos para que cuando haya 3 pidiendo ayuda, despierten a Santa.  
- *Bloques `synchronized` (MUTEX)*: Se usan para modificar variables compartidas de forma segura.  

