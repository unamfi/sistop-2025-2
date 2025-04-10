import javax.swing.*;
import java.awt.*;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;

public class EmocionesP extends JPanel {
    private final Map<String, JProgressBar> barras;
    private final Map<String, Emocion> emociones;
    private final ExecutorService executor;
    private final Semaphore semaforo;

    public EmocionesP() {
        setLayout(new BorderLayout());

        String[] nombres = { "alegria", "tristeza", "enojo", "ansiedad" };
        Map<String, Color> colores = Map.of(
                "alegria", Color.YELLOW,
                "tristeza", new Color(70, 130, 180),
                "enojo", Color.RED,
                "ansiedad", new Color(255, 140, 0));

        barras = new HashMap<>();
        emociones = new HashMap<>();
        executor = Executors.newCachedThreadPool();
        semaforo = new Semaphore(4);

        JPanel panelBarras = new JPanel(new GridLayout(nombres.length, 1));
        for (String nombre : nombres) {
            JProgressBar barra = new JProgressBar(0, 100);
            barra.setStringPainted(true);
            barra.setForeground(colores.get(nombre));
            barra.setString(nombre);
            barras.put(nombre, barra);
            panelBarras.add(barra);

            Emocion emocion = new Emocion(nombre, barra, semaforo);
            emociones.put(nombre, emocion);
            executor.submit(emocion);
        }
        add(panelBarras, BorderLayout.CENTER);
    }

    public void procesarEntrada(String texto) {
        texto = texto.toLowerCase();
        if (texto.contains("feliz") || texto.contains("alegria"))
            emociones.get("alegria").activar();
        if (texto.contains("triste") || texto.contains("llorando"))
            emociones.get("tristeza").activar();
        if (texto.contains("enojo") || texto.contains("molesto") || texto.contains("enojado"))
            emociones.get("enojo").activar();
        if (texto.contains("ansioso") || texto.contains("estresado"))
            emociones.get("ansiedad").activar();
    }
}