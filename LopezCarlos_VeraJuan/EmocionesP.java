import javax.swing.*; //Nos ayuda con la interfaz (contiene JFrame, Jpanel, JButton)
import java.awt.*; // Es mejor tenerlo cuando usamos swing 
import java.util.*; //la libreria de toda la vida en java
import java.util.concurrent.*; //contiene ExecutorService, Semaphore, TimeUnit
import java.util.concurrent.locks.*; //Contiene locks, condition 
import java.util.stream.*; // Permite operaciones estilo funcional (filter, map, reduce) sobre secuencias de elementos

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

    private JPanel crearHeaderArcoiris() {
        JPanel headerPanel = new JPanel(new BorderLayout()) {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;

                float[] fractions = { 0f, 0.16f, 0.33f, 0.49f, 0.66f, 0.82f, 1f };
                Color[] colors = {
                        new Color(255, 0, 0), // Rojo
                        new Color(255, 165, 0), // Naranja
                        new Color(255, 255, 0), // Amarillo
                        new Color(0, 128, 0), // Verde
                        new Color(0, 0, 255), // Azul
                        new Color(75, 0, 130), // Índigo
                        new Color(238, 130, 238) // Violeta
                };

                LinearGradientPaint gradient = new LinearGradientPaint(
                        0, 0, getWidth(), 0, fractions, colors);

                g2d.setPaint(gradient);
                g2d.fillRect(0, 0, getWidth(), getHeight());
            }
        };

        JLabel titulo = new JLabel(" F E E L I N G S ", SwingConstants.CENTER);
        titulo.setFont(new Font("Arial", Font.BOLD, 28));
        titulo.setForeground(Color.WHITE);
        titulo.setBorder(BorderFactory.createEmptyBorder(15, 0, 15, 0));
        headerPanel.add(titulo, BorderLayout.CENTER);
        headerPanel.setPreferredSize(new Dimension(0, 60));

        return headerPanel;
    }

    public EmocionesP() {
        setLayout(new BorderLayout());
        setOpaque(false);
        add(crearHeaderArcoiris(), BorderLayout.NORTH);
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

    @Override // Queremos que nuestro titulo se vea bien, entonces no es más que logica para
              // la interfaz
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
        lockEmociones.lock(); // Adquiere un bloqueo (lock) para asegurar que el acceso al mapa de emociones
                              // sea thread-safe (seguro para hilos concurrentes)
        try {
            return emociones.keySet().stream() // Obtiene todas las claves del mapa emociones y las convierte en un
                                               // stream para procesamiento
                    .filter(this::estaEmocionActiva)
                    .collect(Collectors.toSet());
        } finally {
            lockEmociones.unlock();
        }
    }

    public boolean sonCompatibles(Set<String> emocionesAVerificar) { // Método necesario para verificar que las
                                                                     // emociones sean congruentes
        long countGrupo1 = emocionesAVerificar.stream().filter(grupo1::contains).count(); // Filtra solo las emociones
                                                                                          // que están contenidas en
                                                                                          // grupo1
        if (countGrupo1 > 1)
            return false;

        long countGrupo2 = emocionesAVerificar.stream().filter(grupo2::contains).count();
        if (countGrupo2 > 1)
            return false;

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
        lockEmociones.lock(); // Bloquea para acceso thread-safe
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

            if (!this.sonCompatibles(emocionesAActivar)) {
                mostrarErrorIncompatibilidad();
                return;
            }

            for (String emocion : emocionesAActivar) {
                desactivarIncompatibles(emocion);
                emociones.get(emocion).activar(); // Activa la emoción actual
            }

            for (String emocion : emociones.keySet()) {
                barras.get(emocion).setValue(estaEmocionActiva(emocion) ? 100 : 0);
            }

            emocionesCompatibles.signalAll(); // Notifica a otros hilos
        } finally {
            lockEmociones.unlock(); // Siempre libera el lock
        }
    }

    private void desactivarIncompatibles(String emocionActivada) {
        for (String emo : emociones.keySet()) { // Va a recorrer todas las emcociones existentes
            if (!emo.equals(emocionActivada)) { // aquí claramente no se puede comparar consigo misma
                Set<String> conjunto = Set.of(emocionActivada, emo);
                if (!sonCompatibles(conjunto)) {
                    emociones.get(emo).desactivarForzado(); // Si son incompatibles, desactiva forzosamente la otra
                                                            // emoción la que no es la que se está activando
                }
            }
        }
    }

    public void mostrarErrorIncompatibilidad() { // Mnadamos a mensaje diciendo de forma comprensiva, si puede tener ese
                                                 // conflicto de emociones
        SwingUtilities.invokeLater(() -> JOptionPane.showMessageDialog(this,
                "¿Estas seguro de sentirte así?", "Error",
                JOptionPane.ERROR_MESSAGE));
    }

    public boolean estaEmocionActiva(String nombreEmocion) {
        lockEmociones.lock(); // Adquiere un lock para garantizar exclusión mutua
        try {
            Emocion emocion = emociones.get(nombreEmocion);
            return emocion != null && emocion.activa; // Accedemos al mapa emociones para recuperar el objeto Emocion
        } finally {
            lockEmociones.unlock(); // Garantiza que el lock se libere incluso si falla la operación y evita
                                    // deadlocks o bloqueos permanentes
        }
    }

    public void liberarPermiso() { // Este método es extremadamente simple pero cumple una función importante en la
        semaforoGlobal.release(); // gestión de concurrencia del sistema, su acción principal es libera un permiso
                                  // (unidad de acceso)
    } // en el semáforo global del sistema. El efecto es que incrementa el contador
      // interno del semaforo
      // Si hay hilos esperando por un permiso, uno de ellos podrá continuar su
      // ejecucion
      // ejecución

    public void shutdown() { // Este método implementa un patrón de apagado controlado para un
                             // ExecutorService, asegurando la terminación ordenada de los hilos en ejecucion
        executor.shutdownNow(); // Intenta detener todas las tareas en ejecución y cancela tareas pendientes no
                                // iniciadas
        try {
            if (!executor.awaitTermination(1, TimeUnit.SECONDS)) { // Da 1 segundo para terminación ordenada
                                                                   // awaitTermination devuelve false si timeout ocurre
                                                                   // antes que termine
                System.err.println("Advertencia: No todos los hilos terminaron a tiempo");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt(); // Restablecemos flag de interrupcion
        }
    }
}