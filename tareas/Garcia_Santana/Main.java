import java.util.Scanner;
import java.util.concurrent.Semaphore;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.BrokenBarrierException;
import java.util.Random;



class Elfo extends Thread {
    private Santa santa;
    private CyclicBarrier barrera;

    public Elfo (Santa santa, CyclicBarrier barrera) {
        this.santa = santa;
        this.barrera = barrera;
    }

    public void run() {
        while (!this.santa.despierto) {
            try {
                System.out.println("Elfo "+this.getId()+": Estoy trabajando freneticamente...");
                this.sleep(3000);
                this.pedirAyuda();
                this.sleep(3000);
            } catch (InterruptedException e) {
                System.out.println("Ocurrio una InterruptedException");
            }
        }
    }

    public void pedirAyuda() {
        System.out.println("Elfo "+this.getId()+": ¡¡¡Ayudame santa!!!");
        try {
            this.santa.semaforo.acquire();
            synchronized (this) {
                this.santa.curr_elfos += 1;
            }
            while (!this.santa.despierto) {
                if (this.santa.curr_elfos == this.santa.max_elfos) {              
                    if (this.santa.curr_renos == 9) {
                        this.santa.despierto = true;
                        System.out.println("Santa ha despertado.");
                        break;
                    }

                    barrera.await();
                    this.santa.ayudar(this.getId());
                    break;
                }
                else {
                    if (this.santa.curr_renos == 9) {
                        this.santa.despierto = true;
                        System.out.println("Santa ha despertado.");
                        break;
                    } 
                    this.sleep(3000);
                }
            }
        } catch (InterruptedException e1) {
            System.out.println("El metodo 'pedirAyuda' de la clase 'Elfo' fallo por una interrupcion.");
        } catch (BrokenBarrierException e2) {
            System.out.println("El metodo 'pedirAyuda' de la clase 'Elfo' fallo por BrokenBarrier.");
        }
    }

}

class Reno extends Thread {
    private Santa santa;

    public Reno (Santa santa) {
        this.santa = santa;
    }

    public void run() {
        Random random = new Random();
        int numeroEntero = random.nextInt(10) + 1;
        int contador = 0;
        while (contador < numeroEntero) {
            System.out.println("Estoy vacacionando :). Soy el reno: "+this.getId());
            try {
                this.sleep(1000);
                contador++;
            } catch (InterruptedException e) {
                System.out.println("Ocurrio una InterruptedException");
            }
        }
        this.regresar();   
        synchronized (this) {
            this.santa.curr_renos++; 
        }
    }

    public void regresar() {
        System.out.println("Hola, he vuelto. Soy el reno "+this.getId());
    }

}


class Santa {
    static Semaphore semaforo;
    static final int max_elfos = 3; // numero de permisos
    static int curr_elfos = 0;
    static int curr_renos = 0;
    static boolean despierto = false;

    public Santa() {
        semaforo = new Semaphore(max_elfos);
    }

    public void ayudar(long id) {
        synchronized (this) {
            System.out.println("Tranquilos chavos, ya llegue. Ayudando al elfo "+id);
            curr_elfos--;
        }
        semaforo.release();
    }

}

public class Main {
    public static void main(String[] args) throws InterruptedException {

        int max_elfos = 3;
        CyclicBarrier barrera = new CyclicBarrier(max_elfos, () -> {
            System.out.println("Ya hay 3 elfos muriendo. Pidiendo ayuda...");
        });
        
        Scanner scanner = new Scanner(System.in);
        int n_elfos, n_renos = 9;
        Santa santa = new Santa();

        System.out.print("Ingresa el numero de elfos: ");
        n_elfos = scanner.nextInt();
        scanner.nextLine();

        Reno[] renos = new Reno[n_renos];
        for (int i=0; i<n_renos; i++) {
            renos[i] = new Reno(santa); // Crear un hilo
            renos[i].start();
        }

        Elfo[] elfos = new Elfo[n_elfos];
        for (int i=0; i<n_elfos; i++) {
            elfos[i] = new Elfo(santa, barrera);
            elfos[i].start();
        }

        scanner.close();
    }
}






