import java.util.Scanner;

public class HolaAnuar {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Ingrese su nombre\n");
        String nombre = scanner.nextLine();
        System.out.println("Hola " + nombre);
        scanner.close();
    }
}