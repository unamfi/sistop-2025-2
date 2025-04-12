# Proyecto 1: Don Rata

## Planteamiento del problema
Dentro de la facultad es normal que en un día normal de clases,a los alumnos se nos olvide traer los materiales, la bata o las impresiones que van a ser requeridas para una clase. Por lo que nos vemos en la sitaución desesperada de acudir a "Don Rata". Sin embargo, como a muchos en el anexo de Ingenieria les pasa esta situación, Don Rata no puede darse abasto a todos los alumnos que acuden a su local y muchas veces el orden con el que llegas no es el mismo orden en el que te atienden, aunque casi siempre te atienden si ven que llevas mucho tiempo esperando.

En don rata usualemente suelen trabajar tres persona, por lo que cada uno de ellos puede atender solo a una persona a la vez, es decir el estudiante que llegue mientras los trabajadores están atendiendo a otro debe esperar como todos. Ya que si no lo hace puede desatar una confusión entre Don Rata y los pedidos de los alumnos. Por supuesto que si un estudiante ve un cupo vacío, no dudará en tomarlo.

## Problemas de Concurrencia
1. **Condición de carrera**: Si dos o más estudiantes intentan acceder al mismo trabajador al mismo tiempo, puede que los pedidos se confundan. De igual forma, el estudiante puede querer ser atendido aún cuando
ninguno trabajador esta disponible, lo que obviamente es una situación ilógica.
2. **Espera Activa**: Si no hay estudiantes que atender, es una buena práctica que los hilos trabajadores se bloqueen hasta que llegue un estudiante. De igual forma, si no hay disponibilidad el estudiante debe esperar.
3. **Inanición**: Al existir muchos estudiantes en la fila y Don Rata solo puede atender a 3 a la vez, algunos estudiantes pueden quedar esperando por mucho tiempo.

## Eventos secuenciales

En nuestra interfaz, existe un solo evento que deseamos que lleve un poco de orden. Este es que el alumno y trabajador esten sincronizados, no nos agrada que un trabajador señalice que esta ocupado, sin antes ver que hay un alumno, es decir, queremos que el alumno se vea primero con el trabajador y que luego este indique que esta ocupado.

## Mecanismos de sincronización
Para solucionar evitar los efectos nocivos de la concurrencia se siguió la siguiente lógica de desarrollo utilizando exclusivamente semáforos:

- Se utilizaron semáforos tipo mutex con la finalidad de proteger algunas variables importantes como el id de nuestro estudiante y el acceso a las coordenadas de los trabajadores.

- Para evitar problemas con la espera activa, los trabajadores permanecen bloqueados hasta que llegue un alumno que necesite ser atendido. Esto ahorra recursos y sigue las buenas prácticas. De igual manera, si no hay
disponibilidad se bloquean los alumnos. Ambas perspectivas siguen los principios de un torniquete, aunque
la implementación fue diferente.

- Con el fin de reducir la posibilidad de inanición, se implementó una especie de cola de trabajadores disponibles. De esta forma, los alumnos van tomando al trabajador que esté libre a medida que llegan.

- Se implementó el mecanismo rendezvous para que el trabajador señalice que esta ocupado una vez que 
  el alumno se muestre en la interfaz gráfica.

## Lógica de Operación

Las variables de estado compartido que no son parte de los semáforos son:

- contador: Sirve como el id global del estudiante
- available: Esta cola almacena los id's de los trabajadores que esten disponibles
- queries: Esta cola guarda todos los cambios que la UI debe ejecutar


### Flujo de trabajo
1. El trabajador permanece bloqueado hasta que reciba una solicitud de un alumno.
2. Durante este tiempo, se encuentra en la cola de disponibilidad el id de algún trabajador disponible.
3. Un alumno lo toma de esa cola y lo despierta para que lo atienda.
4. Se configura la figura del alumno en la posición del trabajador
5. Se configura el cambio de señalización del trabajador
6. Se guardan las actualizaciones pertinentes a la UI en la cola de actualizaciones
7. Cuando termine de atenderlo este vuelve a añadirse a la cola de disponibilidad y permanece así hasta que llegue otro alumno.

### Descripción Algorítmica
Existen 4 tipos de hilos relevantes en nuestro programa
- El hilo main: Este hilo es responsable de sostener la interfaz gráfica de nuestro programa.
  - Se inicializan los objetos tk y canvas, responsables de administrar la UI. 
  - Se accede al método setup_ui
  - Se crea la ventana de la interfaz, junto con un botón de salida
  - Se instancia el objeto TiendaSprite, el cual genera la imagen de la tienda y los trabajadores
  - Crea el hilo reponsable de iniciar el lanzamiento de varios hilos
  - Accede al método de hearing donde se revisa y en en caso de existir, se ejecutan las actualizaciones a la 
    UI por parte de los hilos
- El hilo inicio
  - En un ciclo se crean todos los hilos trabajadores
  - En otro ciclo ciclo se crean alumnos indefinidamente, para no exceder la cantidad de hilos permitidos
    por python, se establece una instrucción de time.sleep() entre cada lanzamiento
- Los hilos workers
  - Responsables de atender los pedidos.
  - Mantiene la bandera de disponibilidad en blanco
  - Se bloquean al inicio hasta que un alumno requiere de una solicitud a través de un torniquete
  - Al desbloquearse coloca la bandera en ocupado
  - Se bloquea hasta que el alumno termine su pedido

- Los hilos alumnos
  - Espera a que un trabajador este disponible y después saca de la cola available el id del trabajador.
  - Desbloquean a cualquier hilo trabajador disponible
  - Configura el disfraz del alumno
  - Manda la actualización a la cola de actualizaciones
  - Al realizar el pedido se elimina, aunque antes espera un tiempo variable, esto fue con el propósito de que se visualizarán alumnos al mismo tiempo.
  - Coloca el hilo trabajador como disponible al finalizar


## Entorno de Desarrollo

### Lenguaje

Utilizamos Python 3.11.2

### Bibliotecas y herramientas utilizadas
- `threading`: Para manejar los hilos de los estudiantes y trabajadores.
- `queue`: Para manejar la cola de estudiantes que esperan ser atendidos. Las colas producidas por 
           esta biblioteca son Thread Safe, por lo que no es necesaria protegerlas con mecanismos de sincronización
- `random`: Para simular el tiempo de espera y el tiempo de atención.
- `tkinter`: Para crear la interfaz gráfica de usuario (GUI) que simula la tienda de Don Rata.
- `math`: Para realizar cálculos en a la ubicación de un objeto dentro de la interfaz.

### Ejecución
Para ejecutar el programa, simplemente ejecute el archivo `interfaz.py` que se encuentra dentro de la carpeta de frontend. Asegúrese de tener instaladas las bibliotecas necesarias.
```bash
sudo apt-get install python3-tk
```
Si usa un sistema basado en Red Hat como Fedora, use el siguiente comando:
```bash
sudo dnf install python3-tkinter
```
En caso de que se desee una salida por terminal únicamente se ejecutaría el archivo `sincronization.py`

### Sistema Operativo

Probamos nuestro programa en los sistemas operativos linux mint y fedora.

## Ejemplos

![Imagen de Ejecución de la interfaz](img/imagenEjecucion.png)

El programa es ejecutado con el comando proporcionado anteriormente, mostrandonos de inmediato la interfaz realizada en este proyecto con la finalidad de representar de mejor manera la tienda de Don Rata.

![Imagen de Ejecución de la interfaz](img/resultadoEjecucion.png)

Como puede observarse en la imagen el programa simula la tienda de Don Rata, donde los trabajadores son representados con un circulo rojo y los alumnos con un semicirculo rosado y un cuadro que representa su cuerpo. Además de que se añadieron pequeñas animaciones para simular el flujo de alumnos que tiene Don Rata a lo largo de un día. Finalmente tambien incluye un boton con el cual puede detenerse la ejecución del programa en caso de que se desee.