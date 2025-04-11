
# Trolebús. Una situación cotidiana con concurrencia y sincronización

_Materia_: Sistemas Operativos

_Semestre_: 2025-2

_Alumnos:_ 

Membrilla Ramos Isaias Iñaki

Miramón Pérez Jocelyn  

_Grupo_: 6


## Problema planteado 
Un problema para abordar la concurrencia y la sincronización en primera instancia fue el uso del pumabus, ya que, siempre hay bastantes usuarios queriendo abordar, pero además de que solo en el metro CU se respetan las líneas y estar formados, no encontramos alguna otra regla, más que subir en las paradas establecidas, por lo que, pensamos que en el día a día también usamos el transporte público, específicamente un trolebús, este camión azul tiene algunas características: 

- **Espacio mixto**  
  - Asientos comunes
  - Asientos reservados 
  - Espacio personas paradas 
- **Espacio exclusivo para mujeres**  
  - Asientos para mujeres  
  - Espacio mujeres paradas  

Además también encontramos y establecimos que suben personas de distintos perfiles:

- Mujeres  
- Mujeres de la tercera edad, embarazadas o con alguna comorbilidad  
- Hombres de la tercera edad, embarazadas o con alguna comorbilidad  
- Hombres  

Estos perfiles ejecutan acciones como: **buscar asiento, pararse, bajarse**. En la simulación se tendrá en cuenta que el camión comienza vacío y realiza paradas para subir y bajar pasajeros.

### Reglas de la simulación concurrente

- **Asientos reservados**:  
  Solo pueden ser ocupados por mujeres y hombres de la tercera edad, embarazadas o con alguna comorbilidad. Pero ambos perfiles pueden ocupar cualquier asiento.

- **Espacio mixto**:  
  Persona de la tercera edad, embarazadas o con alguna comorbilidad: si no encuentra asiento libre o reservado no se sube.  
  Las mujeres y los hombres pueden ocupar cualquier lugar, excepto asientos reservados.

- **Espacio exclusivo**:  
  Los hombres no pueden ocupar la zona exclusiva de mujeres.


Las consecuencias nocivas de la concurrencia en esta situación es que existe una mala gestión en el transporte público, si excedes la capacidad no podrás subirte o hasta exponer tu integridad. Los eventos que queremos contralar son; respetar los asientos reservados, y asignar a cada persona un lugar sin exceder la capacidad del transporte. En este caso, importa el orden de como se van formando los pasajeros. 


## Descripción de los mecanismos de sincronización empleados. 

 Los mecanismos que se utilizaron para resolver el problema son __semáforos__ para que los usuarios suban en orden, cada usuario representa un hilo que nace a partir de oprimir un botón. Además para la representación de cada estación se utilizan barreras para los espacios que se ocupan, y los que se liberan. 
 
**Lógica de operación** 
- Global
    - listaAsientos[]
        La lista de asientos una estructura global, ya que cada hilo puede leer para ver la disponibilidad y además escribir en ella (0-libre, 1-ocupado). 
    - estacionCamion 
      Contador para la estacionCamion
    - color
        Se utiliza para cambiar en las funciones el color de los pasajeros asociados a cada perfil. 
    - Variables gráficas (xUsuario, yUsuario)
     Se utilizan para dibujar los elemetos de la interfaz gráfica. 
            - hombre : rojo
            - mujer : azul 
            - hombre mayor: verde
            - mujer mayor : amarillo 

            
- Descripción algorítmica del avance de cada hilo 
    - Hilo pasajero. Cuenta con un mutex el cual evita concurrencia al momento de utilizar la lista de asientos, después espera otro mutex el cual le indica si se encuentra en su parada
    - Hilo principal. El hilo principal se encarga del apartado gráfico y libera los mutex que indican en qué parada se encuentra

- Descripción de la interacción entre los hilos
    La interacción entre hilos  pasajeros es con un mutex para indicar si puede modificar la lista de asientos La interacción entre hilos pasajeros y el hilo main es que el hilo main le indica al hilo pasajero si se encuentra en su parada utilizando un agente. 

## Descripción del entorno de desarrollo 
- Lenguaje 
El lenguaje utilizado es python, para ello debemos garantizar que tenemos la versión 3 instalada, se puede verificar con: 

`python --version`

- Bibliotecas: 
Las bibliotecas utilizadas son estándar, por lo que, no necesitamos instalar nada más, estas fueron: 
``` python
from tkinter import * 
from tkinter import messagebox 
import threading 
import time 
```

- Sistema operativo 
    El sistema donde hicimos el programa y las pruebas de ejecución fue Windows 10. 

## Pruebas de ejecución
![Prueba](/images/prueba1.png)

