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
        lock.lock();
        try {
            if (!activa) {
                activa = true;
                forzarDesactivar = false;
                emocionesCompatibles.signalAll();
            }
        } finally {
            lock.unlock();
        }
    }

    public void desactivarForzado() {
        lock.lock();
        try {
            if (activa) {
                forzarDesactivar = true;
                emocionesCompatibles.signalAll();
            }
        } finally {
            lock.unlock();
        }
    }

    @Override
    public void run() {
        while (!Thread.currentThread().isInterrupted()) {
            try {
                lock.lock();
                try {
                    while (!esCompatible()) {
                        if (activa) {
                            activa = false;
                            panel.liberarPermiso();
                        }
                        emocionesCompatibles.await(100, TimeUnit.MILLISECONDS);
                    }

                    if (forzarDesactivar) {
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
                Thread.sleep(50);
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

        if (!forzarDesactivar && intensidad >= 100) {
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
                try {
                    if (activa) {
                        activa = false;
                        panel.liberarPermiso();
                    }
                } finally {
                    lock.unlock();
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

        // Obtener todas las emociones activas (excepto esta)
        Set<String> emocionesActivas = panel.getEmocionesActivas();
        emocionesActivas.remove(nombre);

        // Crear conjunto con nuestra emoción + las activas
        Set<String> conjuntoAVerificar = new HashSet<>(emocionesActivas);
        conjuntoAVerificar.add(nombre);

        return panel.sonCompatibles(conjuntoAVerificar);
    }
}