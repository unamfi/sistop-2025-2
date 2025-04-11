import javax.swing.*;
import java.awt.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;
import java.util.stream.*;

public class EmocionesP extends JPanel {
    private final Map<String, JProgressBar> barras;
    private final Map<String, Emocion> emociones;
    private final ExecutorService executor;
    private final Lock lockEmociones;
    private final Condition emocionesCompatibles;
    private final Semaphore semaforoGlobal = new Semaphore(3, true);

    private final Set<String> grupo1 = Set.of("alegria", "tristeza", "enojo");
    private final Set<String> grupo2 = Set.of("ansiedad", "calma");

    private final Color[] coloresArcoiris = {
            new Color(255, 50, 50, 40), // Rojo
            new Color(255, 150, 50, 40), // Naranja
            new Color(255, 255, 50, 40), // Amarillo
            new Color(50, 255, 50, 40), // Verde
            new Color(50, 150, 255, 40), // Azul
            new Color(100, 50, 255, 40), // Índigo
            new Color(200, 50, 255, 40) // Violeta
    };

    public EmocionesP() {
        setLayout(new BorderLayout());
        setOpaque(false);

        String[] nombres = { "alegria", "tristeza", "enojo", "ansiedad", "calma" };
        Map<String, Color> coloresEmociones = Map.of(
                "alegria", new Color(30, 144, 255),
                "tristeza", new Color(70, 40, 100),
                "enojo", new Color(220, 20, 60),
                "ansiedad", new Color(204, 85, 0),
                "calma", new Color(50, 205, 50));

        barras = new HashMap<>();
        emociones = new HashMap<>();
        executor = Executors.newFixedThreadPool(nombres.length);
        lockEmociones = new ReentrantLock();
        emocionesCompatibles = lockEmociones.newCondition();

        JPanel panelBarras = new JPanel(new GridLayout(nombres.length, 1, 10, 10));
        panelBarras.setOpaque(false);

        for (String nombre : nombres) {
            JProgressBar barra = new JProgressBar(SwingConstants.VERTICAL, 0, 100) {
                @Override
                protected void paintComponent(Graphics g) {
                    Graphics2D g2d = (Graphics2D) g.create();

                    g2d.setColor(new Color(240, 240, 240, 220));
                    g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 15, 15);

                    int altura = (int) (getHeight() * (getValue() / 100.0));
                    g2d.setColor(getForeground());
                    g2d.fillRoundRect(3, getHeight() - altura, getWidth() - 6, altura, 10, 10);

                    g2d.setColor(getForeground().darker().darker());
                    g2d.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 15, 15);

                    g2d.setColor(Color.BLACK);
                    g2d.setFont(new Font("Arial", Font.BOLD, 12));
                    FontMetrics fm = g2d.getFontMetrics();
                    String texto = getString();
                    int x = (getWidth() - fm.stringWidth(texto)) / 2;
                    int y = (getHeight() + fm.getAscent()) / 2 - 2;
                    g2d.drawString(texto, x, y);

                    g2d.dispose();
                }
            };

            barra.setStringPainted(true);
            barra.setForeground(coloresEmociones.get(nombre));
            barra.setString(nombre);
            barra.setBorder(BorderFactory.createEmptyBorder(5, 10, 5, 10));
            barras.put(nombre, barra);
            panelBarras.add(barra);

            Emocion emocion = new Emocion(nombre, barra, lockEmociones, emocionesCompatibles,
                    grupo1, grupo2, this);
            emociones.put(nombre, emocion);
            executor.submit(emocion);
        }

        add(panelBarras, BorderLayout.CENTER);
    }

    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);

        Graphics2D g2d = (Graphics2D) g.create();
        int width = getWidth();
        int height = getHeight();
        int bandHeight = height / coloresArcoiris.length;

        for (int i = 0; i < coloresArcoiris.length; i++) {
            g2d.setColor(coloresArcoiris[i]);
            g2d.fillRect(0, i * bandHeight, width, bandHeight);

            if (i < coloresArcoiris.length - 1) {
                GradientPaint gp = new GradientPaint(
                        0, i * bandHeight + (bandHeight / 2), coloresArcoiris[i],
                        0, (i + 1) * bandHeight, coloresArcoiris[i + 1]);
                g2d.setPaint(gp);
                g2d.fillRect(0, i * bandHeight + (bandHeight / 2), width, bandHeight / 2);
            }
        }
        g2d.dispose();
    }

    public Set<String> getEmocionesActivas() {
        lockEmociones.lock();
        try {
            return emociones.keySet().stream()
                    .filter(this::estaEmocionActiva)
                    .collect(Collectors.toSet());
        } finally {
            lockEmociones.unlock();
        }
    }

    public boolean sonCompatibles(Set<String> emocionesAVerificar) {
        // Verificar incompatibilidades dentro del grupo1
        long countGrupo1 = emocionesAVerificar.stream().filter(grupo1::contains).count();
        if (countGrupo1 > 1)
            return false;

        // Verificar incompatibilidades dentro del grupo2
        long countGrupo2 = emocionesAVerificar.stream().filter(grupo2::contains).count();
        if (countGrupo2 > 1)
            return false;

        // Verificar reglas cruzadas
        if (emocionesAVerificar.contains("alegria") && emocionesAVerificar.contains("ansiedad"))
            return false;
        if (emocionesAVerificar.contains("enojo") && emocionesAVerificar.contains("ansiedad"))
            return false;
        if (emocionesAVerificar.contains("enojo") && emocionesAVerificar.contains("calma"))
            return false;
        if (emocionesAVerificar.contains("tristeza") && emocionesAVerificar.contains("calma"))
            return false;

        return true;
    }

    public void procesarEntrada(String texto) {
        texto = texto.toLowerCase();
        lockEmociones.lock();
        try {
            Set<String> emocionesAActivar = new HashSet<>();

            // Detectar todas las emociones a activar
            if (texto.contains("feliz") || texto.contains("alegria"))
                emocionesAActivar.add("alegria");
            if (texto.contains("triste") || texto.contains("llorando"))
                emocionesAActivar.add("tristeza");
            if (texto.contains("enojo") || texto.contains("molesto") || texto.contains("enojado"))
                emocionesAActivar.add("enojo");
            if (texto.contains("ansioso") || texto.contains("estresado"))
                emocionesAActivar.add("ansiedad");
            if (texto.contains("calmado") || texto.contains("tranquilo"))
                emocionesAActivar.add("calma");

            // Verificar compatibilidad
            if (!this.sonCompatibles(emocionesAActivar)) {
                mostrarErrorIncompatibilidad();
                return;
            }

            // Desactivar incompatibles y activar las nuevas
            for (String emocion : emocionesAActivar) {
                desactivarIncompatibles(emocion);
                emociones.get(emocion).activar();
            }

            // Actualizar barras
            for (String emocion : emociones.keySet()) {
                barras.get(emocion).setValue(estaEmocionActiva(emocion) ? 100 : 0);
            }

            emocionesCompatibles.signalAll();
        } finally {
            lockEmociones.unlock();
        }
    }

    private void desactivarIncompatibles(String emocionActivada) {
        // Desactivar todas las emociones incompatibles
        for (String emo : emociones.keySet()) {
            if (!emo.equals(emocionActivada)) {
                Set<String> conjunto = Set.of(emocionActivada, emo);
                if (!sonCompatibles(conjunto)) {
                    emociones.get(emo).desactivarForzado();
                }
            }
        }
    }

    public void mostrarErrorIncompatibilidad() {
        SwingUtilities.invokeLater(() -> JOptionPane.showMessageDialog(this,
                "¿Estas seguro de sentirte así?", "Error",
                JOptionPane.ERROR_MESSAGE));
    }

    public boolean estaEmocionActiva(String nombreEmocion) {
        lockEmociones.lock();
        try {
            Emocion emocion = emociones.get(nombreEmocion);
            return emocion != null && emocion.activa;
        } finally {
            lockEmociones.unlock();
        }
    }

    public void liberarPermiso() {
        semaforoGlobal.release();
    }

    public void shutdown() {
        executor.shutdownNow();
        try {
            if (!executor.awaitTermination(1, TimeUnit.SECONDS)) {
                System.err.println("Advertencia: No todos los hilos terminaron a tiempo");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}