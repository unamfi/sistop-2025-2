# Ejercicio Elevador

**Autores:** Salazar Islas Luis Daniel y Tepal Briseño Hansel Yael

## Entorno

Desarrollamos nuestra solución en Python utilizando las bibliotecas `threading` y `random`. Para ejecutar el programa, solo es necesario correr el siguiente comando:

```bash
python3 problemaAscensor.py
```
Para observar la salida completa del programa, se recomienda redirigir la salida a un archivo de texto y revisarlo posteriormente con grep o un editor de texto:

```bash
python3 problemaAscensor.py > salida.txt
```
Para detener el programa, se debe utilizar `Ctrl + C`.


## Solución

Nuestra implementación del ascensor sigue esta lógica:

- Al inicio, el ascensor espera a ser llamado por un usuario.
- Cuando un usuario llama al ascensor, este se dirige a su piso según la política. Una vez que llega, el usuario sube si esta disponible.
- El ascensor se dirige al piso de destino del usuario.
- Cuando llega al destino, los usuarios que desean bajar en ese piso bajan y los que deseen subir lo hacen siempre y cuando se respeta la disponibilidad.

Para simular el movimiento del ascensor, utilizamos varios arreglos del tamaño del número de pisos:
- Un arreglo lleva la cuenta de los usuarios que esperan en cada piso.
- Otro arreglo cuenta los usuarios dentro del ascensor y sus destinos.
- Se utilizan dos arreglos de mutex para proteger el acceso a estas estructuras.

El ascensor opera en un hilo propio que maneja su movimiento mediante:
- Un semáforo.
- Una variable que cuenta las solicitudes.
- Un mutex para proteger estas variables y evitar conflictos.

Cada vez que un usuario solicita el ascensor:
- El semáforo se incrementa y la variable de solicitudes aumenta en 1.
- Cuando el usuario llega a su destino, la variable de solicitudes se decrementa.
- Si no hay solicitudes pendientes, el ascensor deja de moverse y el semáforo se decrementa hasta que haya una nueva solicitud.

Importante aclarar que esto no elimina por completo la espera activa del elevador para las solicitudes, pero lo disminuye bastante.

La lógica de movimiento se basa en dos direcciones: una hacia el piso más alto solicitado y otra hacia el más bajo. Cuando el ascensor llega al extremo de su recorrido, cambia de dirección. Si un usuario hace una nueva solicitud, la dirección se actualiza. Dos mutex protegen la actualización de direcciones. Esto se realizó debido a que si dos usuarios desean subir, el elevador únicamente debe dirigirse al piso más alto, puesto que pasará por los otros pisos por defecto. La misma lógica aplica a si dos usuarios desean bajar.

Para gestionar la entrada y salida de los usuarios:
- Se usa un torniquete para asegurarse de que los usuarios suban o bajen solo cuando el elevador pasa por el piso.
- Un multiplex limita el número de personas dentro del ascensor a un máximo de 5.

## Problemas encontrados

- Durante la impresión de mensajes, notamos que los textos de los usuarios no siempre están perfectamente sincronizados con el movimiento del ascensor. Esto no afecta el funcionamiento general, ya que los usuarios bajan donde deben, pero no pudimos solucionar completamente el problema. Intentamos varias técnicas de sincronización como el Rendezvous, pero en algunos casos bloqueaba el ascensor por completo. 😕

- Una posible mejora sería evitar la inanición de los usuarios esperando al ascensor. Para ello, podríamos dividir la lógica en dos hilos: uno para decidir a qué piso ir y otro para mover el ascensor. Esto podría hacer que la operación sea más eficiente y equitativa. Esto no se implemento por lo que decidimos acotar el numero de usuarios a 50 personas.