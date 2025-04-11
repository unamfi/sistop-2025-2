import javax.swing.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

public class Emocion implements Runnable {
    public volatile boolean activa;
    private volatile boolean forzarDesactivar;
    private int intensidad;
    private final String nombre;
    private final JProgressBar barra;
    private final Lock lock;
    private final Condition emocionesCompatibles;
    private final Set<String> grupo1;
    private final Set<String> grupo2;
    private final EmocionesP panel;

    public Emocion(String nombre, JProgressBar barra, Lock lock, Condition emocionesCompatibles,
            Set<String> grupo1, Set<String> grupo2, EmocionesP panel) {
        this.nombre = nombre;
        this.barra = barra;
        this.lock = lock;
        this.emocionesCompatibles = emocionesCompatibles;
        this.grupo1 = grupo1;
        this.grupo2 = grupo2;
        this.panel = panel;
        this.activa = false;
        this.forzarDesactivar = false;
        this.intensidad = 0;
    }

    public void activar() {
        lock.lock(); // Adquiere un lock para exclusión mutua y garantiza que solo un hilo modifique
                     // el estado a la vez
        try {
            if (!activa) {
                activa = true;
                forzarDesactivar = false; // Limpia cualquier estado de desactivación forzada
                emocionesCompatibles.signalAll(); // Despierta todos los hilos esperando en esta condición
            }
        } finally {
            lock.unlock();
        }
    }

    public void desactivarForzado() {
        lock.lock();
        try {
            if (activa) {
                forzarDesactivar = true; // Establece el flag forzarDesactivar a verdadero e indica que la emoción debe
                                         // ser desactivada prioritariamente
                emocionesCompatibles.signalAll();
            }
        } finally {
            lock.unlock();
        }
    }

    @Override
    public void run() {
        while (!Thread.currentThread().isInterrupted()) { // Se ejecuta continuamente hasta que el hilo es interrumpido
            try {
                if (!lock.tryLock(100, TimeUnit.MILLISECONDS)) {
                    continue;
                }
                try {
                    while (!esCompatible()) {
                        if (activa) {
                            activa = false;
                            panel.liberarPermiso(); // Si está activa, la desactiva y libera permisos, espera
                                                    // notificaciones (hasta 100ms) antes de revalidar
                        }
                        emocionesCompatibles.await(100, TimeUnit.MILLISECONDS);
                    }

                    if (forzarDesactivar) { // Libera recursos si estaba activa
                        if (activa) {
                            panel.liberarPermiso();
                            activa = false;
                        }
                        forzarDesactivar = false;
                        continue;
                    }

                    if (activa) {
                        aumentarIntensidad();
                    } else {
                        disminuirIntensidad();
                    }
                } finally {
                    lock.unlock();
                }
                Thread.sleep(50); // Espera 50ms entre ciclos para reducir carga CPU
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }

    private void aumentarIntensidad() throws InterruptedException {
        for (int i = intensidad; i <= 100 && !forzarDesactivar; i += 5) {
            intensidad = i;
            actualizarBarra();
            Thread.sleep(50);
        }

        if (!forzarDesactivar && intensidad >= 100) { // Adquiere lock para thread-safety y desactiva la emoción,
                                                      // también cambia flag activa
                                                      // y libera permiso asociado, donde libera el lock en bloque
                                                      // finally
            lock.lock();
            try {
                activa = false;
                panel.liberarPermiso();
            } finally {
                lock.unlock();
            }
        }
    }

    private void disminuirIntensidad() {
        if (intensidad > 0) {
            intensidad = Math.max(0, intensidad - 2);
            actualizarBarra();

            if (intensidad == 0) {
                lock.lock();
                try { // Bloqueo para modificación segura del estado, si estaba activa, la desactiva
                      // formalmente
                    if (activa) {
                        activa = false;
                        panel.liberarPermiso();
                    }
                } finally {
                    lock.unlock(); // garantiza la liberacion del lock
                }
            }
        }
    }

    private void actualizarBarra() {
        SwingUtilities.invokeLater(() -> {
            barra.setValue(intensidad);
            barra.setString(nombre + " (" + intensidad + "%)");
        });
    }

    private boolean esCompatible() {
        if (!activa && !forzarDesactivar) {
            return true;
        }

        Set<String> emocionesActivas = panel.getEmocionesActivas();
        emocionesActivas.remove(nombre);

        Set<String> conjuntoAVerificar = new HashSet<>(emocionesActivas);
        conjuntoAVerificar.add(nombre);

        return panel.sonCompatibles(conjuntoAVerificar);
    }
}