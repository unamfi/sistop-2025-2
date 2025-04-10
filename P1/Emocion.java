import javax.swing.*;
import java.util.concurrent.Semaphore;

public class Emocion implements Runnable {
    private final String nombre;
    private final JProgressBar barra;
    private volatile boolean activa;
    private int intensidad;
    private final Semaphore semaforo;

    public Emocion(String nombre, JProgressBar barra, Semaphore semaforo) {
        this.nombre = nombre;
        this.barra = barra;
        this.semaforo = semaforo;
        this.activa = false;
        this.intensidad = 0;
    }

    public void activar() {
        activa = true;
    }

    @Override
    public void run() {
        while (true) {
            try {
                if (activa) {
                    semaforo.acquire();
                    for (int i = 0; i <= 100; i += 10) {
                        intensidad = i;
                        SwingUtilities.invokeLater(() -> barra.setValue(intensidad));
                        Thread.sleep(100);
                    }
                    activa = false;
                    semaforo.release();
                } else {
                    if (intensidad > 0) {
                        intensidad -= 2;
                        SwingUtilities.invokeLater(() -> barra.setValue(intensidad));
                    }
                    Thread.sleep(200);
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    public String getNombre() {
        return nombre;
    }
}