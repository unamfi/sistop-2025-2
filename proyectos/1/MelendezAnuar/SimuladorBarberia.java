// Autores: Meléndez Gómez Anuar, Zambrano Serrano Héctor
//Importación de bibliotecas
import java.util.concurrent.*;
import java.util.Random;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.LinkedList;
import java.util.Queue;


 //Clase principal que representa una barbería con un barbero y sillas de espera.
 // Con esta clase me ayudo para controlar el flujo de clientes y la atención del barbero TONY.
class Barberia {

    // Con esto se me ocurrió establecer la capacidad máxima de espera
    private final int CAPACIDAD_MAXIMA_SILLAS_ESPERA = 3;
    
    //Este semáforo es el encargado de controlar las sillas disponibles (maximo deben de ser 3)
    private final Semaphore sillasDisponibles = new Semaphore(CAPACIDAD_MAXIMA_SILLAS_ESPERA, true);
    
    // Este semaforo lo implemente para controlar si el barbero está disponible (1 = disponible)
    private final Semaphore barberoLibre = new Semaphore(1);
    
    // Lock para proteger el acceso concurrente a la cola de clientes
    private final Lock lockParaColaClientes = new ReentrantLock();
    
    // Lock para proteger el proceso de pago (evitar que dos pagos de lo clientes se puedan mezclar)
    private final Lock lockParaProcesoPago = new ReentrantLock();
    
    // Implemento un generador de números aleatorios para tiempos diferentes
    private final Random generadorAleatorio = new Random();
    
    // Cola que almacena los clientes que estan esperando su turno
    private final Queue<Cliente> clientesEnEspera = new LinkedList<>();
    
    // Indica si el barbero está durmiendo (para no despertarlo múltiples veces)
    private volatile boolean barberoEstaDurmiendo = true;

    /**
     * Método principal para que los clientes entren a la barbería.
     * @param cliente 
     */
    public void clienteEntraABarberia(Cliente cliente) {
        // Bloqueó el acceso a la cola para evitar condiciones de carrera
        lockParaColaClientes.lock();
        try {
            // Verificamos si hay sillas disponibles
            if (clientesEnEspera.size() < CAPACIDAD_MAXIMA_SILLAS_ESPERA) {
                // Si hay sillas disponibles intento ocupar una silla
                if (sillasDisponibles.tryAcquire()) {
                    clientesEnEspera.add(cliente);
                    System.out.println(cliente.obtenerNombre() + " 🪑 Se sienta a esperar. Clientes en espera: " + clientesEnEspera.size());
                    despertarAlBarberoSiEstaDurmiendo();
                }
            } else {
                // No hay sillas disponibles, el cliente se va
                System.out.println(cliente.obtenerNombre() + " No encontró lugar (sillas ocupadas) y se va. 🥲");
            }
        } finally {
            // Siempre libero el lock aunque falle algo
            lockParaColaClientes.unlock();
        }
    }
     // Despierto al barbero para que empiece a chambear :)
     
    private void despertarAlBarberoSiEstaDurmiendo() {
        if (barberoEstaDurmiendo) {
            synchronized (this) {
                // Verificamos doblemente para evitar carreras
                if (barberoEstaDurmiendo) {
                    barberoEstaDurmiendo = false;
                    Barbero.obtenerInstancia().despertar();
                    comenzarAAtenderClientes();
                }
            }
        }
    }

    
    // IniciO la atención de los clientes en un hilo separado.
    
    private void comenzarAAtenderClientes() {
        new Thread(() -> {
            while (true) {
                try {
                    // Con esto analizamos que el barbero este libre
                    barberoLibre.acquire();
                    
                    lockParaColaClientes.lock();
                    try {
                        // Si no hay clientes, el barbero puede dormir(pero regularmente no dormirá porque en horario laboral no se duerme jajas)
                        if (clientesEnEspera.isEmpty()) {
                            barberoLibre.release();
                            ponerAlBarberoADormir();
                            return;
                        }
                        
                        // Tomo el siguiente cliente (el primero en llegar)
                        Cliente clienteActual = clientesEnEspera.poll();
                        // Libero una silla al atender al cliente
                        sillasDisponibles.release();
                        
                        // Proceso de atención al cliente
                        System.out.println("\n🪒 " + clienteActual.obtenerNombre() + " pasa con el barbero 🪒");
                        Barbero barbero = Barbero.obtenerInstancia();
                        barbero.cortarCabello(clienteActual);
                        procesarPago(clienteActual, barbero);
                        barbero.limpiarAreaDeTrabajo();
                    } finally {
                        lockParaColaClientes.unlock();
                    }
                    
                    // Libero al barbero para atender al siguiente cliente
                    barberoLibre.release();
                    // Pequeña pausa entre clientes
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }).start();
    }

    
     //Pone al barbero a dormir cuando no hay clientes.
     
    public void ponerAlBarberoADormir() {
        barberoEstaDurmiendo = true;
        Barbero.obtenerInstancia().dormir();
    }

    /**
     * Procesamos el pago del cliente (operación protegida por lock).
     * @param cliente El cliente que está pagando
     * @param barbero El barbero que recibe el pago
     */
    private void procesarPago(Cliente cliente, Barbero barbero) {
        lockParaProcesoPago.lock();
        try {
            System.out.println(cliente.obtenerNombre() + " 💵 paga a " + barbero.obtenerNombre());
            // Simulamos el tiempo que toma pagar
            Thread.sleep(800 + generadorAleatorio.nextInt(400));
            System.out.println(barbero.obtenerNombre() + " da cambio 💲 a " + cliente.obtenerNombre());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            lockParaProcesoPago.unlock();
        }
    }
}


 //Clase que representa a un cliente de la barbería.

class Cliente implements Runnable {
    private final String nombreCliente;
    private final Barberia barberia;
    private static final Random generadorAleatorio = new Random();

    public Cliente(String nombre, Barberia barberia) {
        this.nombreCliente = nombre;
        this.barberia = barberia;
    }

    public String obtenerNombre() {
        return nombreCliente;
    }

    @Override
    public void run() {
        try {
            // Los clientes llegan en momentos aleatorios
            Thread.sleep(generadorAleatorio.nextInt(1500));
            barberia.clienteEntraABarberia(this);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Clase que representa al barbero (usando patrón Singleton).
 */
class Barbero {
    private static final Barbero instanciaUnica = new Barbero("Tony");
    private final String nombreBarbero;
    private final Random generadorAleatorio = new Random();

    private Barbero(String nombre) {
        this.nombreBarbero = nombre;
    }

    public static Barbero obtenerInstancia() {
        return instanciaUnica;
    }

    public String obtenerNombre() {
        return nombreBarbero;
    }

    /**
     * Método para que el barbero corte el cabello a un cliente.
     * @param cliente El cliente a atender
     */
    public void cortarCabello(Cliente cliente) {
        System.out.println(nombreBarbero + "está cortando ✂️ el cabello de " + cliente.obtenerNombre());
        try {
            // Tiempo de corte variable entre 1.5 y 2.5 segundos
            Thread.sleep(1500 + generadorAleatorio.nextInt(1000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Método para despertar al barbero.
     */
    public void despertar() {
        System.out.println("\n" + nombreBarbero + " ☕️ se despierta y está listo para trabajar!\n");
    }

    /**
     * Método para que el barbero se duerma.
     */
    public void dormir() {
        System.out.println("\n" + nombreBarbero + " 💤 está durmiendo... zZzZz\n");
        try {
            // El barbero duerme 2 segundos
            Thread.sleep(2000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    /**
     * Método para limpiar el área de trabajo.
     */
    public void limpiarAreaDeTrabajo() {
        System.out.println(nombreBarbero + " 🧹 está limpiando la zona de trabajo.");
        try {
            // Tiempo de limpieza variable entre 0.8 y 1.3 segundos
            Thread.sleep(800 + generadorAleatorio.nextInt(500));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}

/**
 * Clase principal que inicia la simulación de la barbería.
 */
public class SimuladorBarberia {
    public static void main(String[] args) {
        Barberia barberia = new Barberia();
        // Pool de hilos para manejar múltiples clientes
        ExecutorService ejecutor = Executors.newCachedThreadPool();

        // Generamos 15 clientes que llegan en intervalos aleatorios
        for (int i = 1; i <= 15; i++) {
            ejecutor.execute(new Cliente("Cliente " + i, barberia));
            try {
                // Intervalos entre 0.3 y 1.0 segundos
                Thread.sleep(300 + new Random().nextInt(700));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        // Apagamos el ejecutor cuando termine
        ejecutor.shutdown();
        try {
            if (!ejecutor.awaitTermination(60, TimeUnit.SECONDS)) {
                ejecutor.shutdownNow();
            }
        } catch (InterruptedException e) {
            ejecutor.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
}