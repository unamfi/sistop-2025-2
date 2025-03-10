//NavaDavid Gpo: 6 SO Practica4

class Hilo extends Thread{
	public Hilo(String nombre){
		super(nombre);
	}
	public void run(){
		for(int i=0;i<5;i++){
			System.out.println("Iteraciòn "+(i+1)+" de "+getName());
		}
		System.out.println("Termina el "+getName());
	}
	public static void main(String[] args) {
		new Hilo("Primer Hilo").start();
		new Hilo("Segundo Hilo").start();
		System.out.println("Termina el hilo principal");
	}
}