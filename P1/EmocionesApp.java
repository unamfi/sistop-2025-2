import javax.swing.*;
import java.awt.*;

public class EmocionesApp extends JFrame {
    public EmocionesApp() {
        super("Sincronía Emocional");
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setSize(500, 400);
        setLayout(new BorderLayout());

        EmocionesP emocionesP = new EmocionesP();
        add(emocionesP, BorderLayout.CENTER);

        JPanel inputPanel = new JPanel(new BorderLayout());
        JLabel label = new JLabel("¿Cómo te sientes hoy?");
        JTextField entrada = new JTextField();
        entrada.addActionListener(e -> {
            emocionesP.procesarEntrada(entrada.getText());
            entrada.setText("");
        });

        inputPanel.add(label, BorderLayout.NORTH);
        inputPanel.add(entrada, BorderLayout.CENTER);
        add(inputPanel, BorderLayout.SOUTH);

        setVisible(true);
    }
}