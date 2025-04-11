from tkinter import *
from tkinter import messagebox
import threading
import time

# Sirve para que se suban en orden
mutex=threading.Semaphore(1) 

# Sirve para que se bajen en la estacion correcta
mutexbaja1=threading.Semaphore(0) 
mutexbaja2=threading.Semaphore(0)
mutexbaja3=threading.Semaphore(0)

listaAsientos=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#variable que nos indica en que estación se encuentra el camion
#esto nos permite que el camion avise en que estación esta
#para que bajen los usuarios 
EstacionCamion=0

# Variables que se utilizan para dibujar los pasajeros
xUsuario=888.0
yUsuario=605.0
xUsuarioFin=910.0
yUsuarioFin=633.0

# Colores utilizados
# hombre='#C41111'
# hombreMayor='#0f6307'
# Mujer='#2600FF'
# MujerMayor='#FFBB00'
color='#000000'

#funcion que revisa si un asiento esta disponible

def revisarAsiento(menor,mayor):
    global color
    if menor<(12):
        for i in range(menor,mayor):
            if listaAsientos[i]==0:
                listaAsientos[i]=1
                asientos(i)
                sentado=1
                return sentado,i
    else:
        for i in range(menor,mayor):
            if listaAsientos[i]==0:
                listaAsientos[i]=1
                dePie(i)
                sentado=1
                return sentado,i
    return 0,0


# Función  que revisa en que asiento se puede sentar
# un pasajero mujer revisa asientos disponibles por prioridad
def mujer(baja):
    global color
    mutex.acquire()
    color='#2600FF'
    sentado=0
    sentado,lugarUtilizado=revisarAsiento(6,12)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(2,6)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(12,14)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(14,16)
    if sentado==0:
        baja=20
        asientos(17)
    window.after(0, persona())
    mutex.release()
    if baja!=20:
        bajar(baja,lugarUtilizado)

# Funcion que revisa en que asiento se puede sentar
# un pasajero mujerMayor revisa asientos disponibles por prioridadad
def mujerMayor(baja):
    global color
    mutex.acquire()
    color='#FFBB00'
    sentado=0
    sentado,lugarUtilizado=revisarAsiento(0,2)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(6,12)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(2,6)
    if sentado==0:
        baja=20
        asientos(17)
    window.after(0, persona())
    mutex.release()
    if baja!=20:
        bajar(baja,lugarUtilizado)

# Funcion que revisa en que asiento se puede sentar
# un pasajero hombre revisa asientos disponibles por prioridad

def hombre(baja):
    print(baja)
    global asientoT,dePieH,color
    mutex.acquire()
    color='#C41111'
    sentado=0
    sentado,lugarUtilizado=revisarAsiento(2,6)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(14,16)
    if sentado==0:
        baja=20
        asientos(17)
    window.after(0, persona())
    mutex.release()
    if baja!=20:
        bajar(baja,lugarUtilizado)

# Funcion que revisa en que asiento se puede sentar
# un pasajero hombreMayor revisa asientos disponibles por prioridad

def hombreMayor(baja):
    global asientoR,asientoT,color
    mutex.acquire()
    color='#0F6307'
    sentado=0
    sentado,lugarUtilizado=revisarAsiento(0,2)
    if sentado==0:
        sentado,lugarUtilizado=revisarAsiento(2,6)
    if sentado==0:
        baja=20
        asientos(17)
    window.after(0, persona())
    mutex.release()
    if baja!=20:
        bajar(baja,lugarUtilizado)
        
#Esta funcion es el pasajero esperando que
#le avisen cuando llega a su estación
#tambien borra su personaje

def bajar(baja, lugarUtilizado):
    global EstacionCamion, color
    if baja==1:
        mutexbaja1.acquire()
        mutexbaja1.release()
    elif baja==2:
        mutexbaja2.acquire()
        mutexbaja2.release()
    elif baja==3:
        mutexbaja3.acquire()
        mutexbaja3.release()
    print("Se baja en estación", EstacionCamion)
    mutex.acquire()
    if lugarUtilizado < 2:
        listaAsientos[lugarUtilizado] = 0
        color = '#88BB69'
        asientos(lugarUtilizado)
        
    elif lugarUtilizado < 6:
        listaAsientos[lugarUtilizado] = 0
        color = '#D9D9D9'
        asientos(lugarUtilizado)
        
    elif lugarUtilizado < 12:
        listaAsientos[lugarUtilizado] = 0
        color = '#FF93C7'
        asientos(lugarUtilizado)

    elif lugarUtilizado < 14:
        listaAsientos[lugarUtilizado] = 0
        color = '#3999FC'
        dePie(lugarUtilizado)

    else:
        listaAsientos[lugarUtilizado] = 0
        color = '#3999FC'
        dePie(lugarUtilizado)

    window.after(0, persona())
    mutex.release()
            
#Funcion que libera los mutex de en que
#estación se encuentran

def avanzar():
    global EstacionCamion,color
    color = '#FFFFFF'
    asientos(17)
    window.after(0, persona())
    print('si jala el boton')
    EstacionCamion += 1
    if EstacionCamion==1:
        mutexbaja1.release()
    elif EstacionCamion==2:
        mutexbaja2.release()
    elif EstacionCamion==3:
# Permite a una persona revisar si le toca bajarse
        mutexbaja3.release()
        time.sleep(1)
        messagebox.showinfo("","El camión ha llegado a la base") 

# Pantalla inicial
def pantallaInicio():
    #Canvas donde se dibuja la app
    #Titulo
    canvas.create_rectangle( 0.0, 0.0, 980.0, 91.0, fill="#121E9C", outline="")
    canvas.create_text(327.0, 24.0, anchor="nw", text="Trolebus", fill="#FFFFFF",font=("Arial", 32))
    #rectangulo del camion
    canvas.create_rectangle( 658.0, 107.0, 945.0, 671.0, fill="#3999FC", outline="")
    #rectangulo asientos y conductor 
    #asiento conductor
    canvas.create_rectangle(880, 600, 920, 640, fill="#D9D9D9", outline="")
    #asiento reservado
    canvas.create_rectangle(880, 520, 920, 560, fill="#88BB69", outline="")
    canvas.create_rectangle(700, 520, 740, 560, fill="#88BB69", outline="")
    #asiento comun
    canvas.create_rectangle(700, 450, 740, 490.0, fill="#D9D9D9", outline="")
    canvas.create_rectangle(880, 450, 920, 490.0, fill="#D9D9D9", outline="")
    canvas.create_rectangle(700, 380, 740, 420.0, fill="#D9D9D9", outline="")
    canvas.create_rectangle(880, 380, 920, 420.0, fill="#D9D9D9", outline="")
    #asiento mujer
    canvas.create_rectangle(700, 310, 740, 350, fill="#FF93C7", outline="")
    canvas.create_rectangle(880, 310, 920, 350, fill="#FF93C7", outline="")
    canvas.create_rectangle(700, 240, 740, 280, fill="#FF93C7", outline="")
    canvas.create_rectangle(880, 240, 920, 280, fill="#FF93C7", outline="")
    canvas.create_rectangle(700, 170, 740, 210, fill="#FF93C7", outline="")
    canvas.create_rectangle(880, 170, 920, 210, fill="#FF93C7", outline="")
    # Conductor
    canvas.create_oval(888, 605, 910, 633, fill="#000000", outline="")
    # Menú desplegable
    canvas.create_text(130, 186, text="Estación destino:", font=("Arial", 16))
    messagebox.showinfo("Instrucciones", " > En la ventana tendremos diferentes botones dependiendo del tipo de perfil que querramos agregar.  \n  "
    " > En la parte superior izquierda se desplegará un menú para asignar en que estación se bajara cada usuario que se agrega \n " 
    " > Para cambiar de estación es necesario usar el botón avanzar")

    
# Funciones que generan los threads se utilizan en los botones
def threadMujer(baja):
    s1 = threading.Thread(target=mujer,args=(baja,))
    s1.start()
def threadHombre(baja):
    s1 = threading.Thread(target=hombre,args=(baja,))
    s1.start()
def threadMujerMayor(baja):
    s1 = threading.Thread(target=mujerMayor,args=(baja,))
    s1.start()    
def threadHombreMayor(baja):
    s1 = threading.Thread(target=hombreMayor,args=(baja,))
    s1.start()

#botones en pantalla    
def botones():
    global var
    button_1 = Button(text="Hombre Mayor", borderwidth=0,
                      highlightthickness=0, command=lambda: threadHombreMayor(int(var.get()),),
                      relief="flat", font=("Ariel", 32))
    button_1.place(    x=40,    y=295,    width=400,    height=50)

    button_2 = Button(text="Hombre", borderwidth=0,
                      highlightthickness=0, command=lambda: threadHombre(int(var.get()),),
                      relief="flat", font=("Ariel", 32))
    button_2.place(    x=40,    y=370,    width=400,    height=50)

    button_3 = Button(text="MujerMayor", borderwidth=0,
                      highlightthickness=0, command=lambda: threadMujerMayor(int(var.get()),),
                      relief="flat", font=("Ariel", 32))
    button_3.place(    x=40,    y=450,    width=400,    height=50)

    button_4 = Button(text="Mujer", borderwidth=0,
                      highlightthickness=0, command=lambda: threadMujer(int(var.get()),),
                      relief="flat", font=("Ariel", 32))
    button_4.place(x=40, y=530, width=400, height=50)
    #se utiliza un thread por que main esta en un loop con el cambas
    button_5 = Button(text="Avanza", borderwidth=0,
                      highlightthickness=0, command=lambda: avanzar(),
                      relief="flat", font=("Ariel", 32))
    button_5.place(x=40, y=600, width=400, height=50)
    
def menudesplegable():
    global var
    var = StringVar(window)  # Crear una StringVar asociada con la ventana
    var.set(1)  # Establecer el valor inicial de la variable
    opciones = [1, 2, 3]  # Las opciones del menú desplegable
    opcion= OptionMenu(window, var, *opciones)  # Crear el menú desplegable
    opcion.config(width=3)  # Configurar el ancho del menú
    opcion.pack(side="top", anchor="w", pady=170, ipadx=20,padx=250)

#dibuja los personajes no se pone dentro de asientos porque lo tiene que ejecutar
#el thread main
def persona():
    global xUsuario,yUsuario,xUsuarioFin,yUsuarioFin
    canvas.create_oval(xUsuario,yUsuario,xUsuarioFin,yUsuarioFin, fill=color, outline="")

# Posición de asientos
def asientos(i):
    global xUsuario,yUsuario,xUsuarioFin,yUsuarioFin
    xUsuario=710.0+180*(i%2)
    yUsuario=525.0-70*(i//2)
    xUsuarioFin=730+180*(i%2)
    yUsuarioFin=555.0-70*(i//2)
    if i==17:
        xUsuario=530
        yUsuario=600
        xUsuarioFin=560
        yUsuarioFin=630
            

# Asigna la posicion y tamaño de los pasajeros
# como al estar de pie tienen una distribucion
# distinta se genero otra función
def dePie(i):
    global xUsuario,yUsuario,xUsuarioFin,yUsuarioFin
    xUsuario=800.0
    yUsuario=200+80*(i-12)
    xUsuarioFin=820.0
    yUsuarioFin=230+80*(i-12)

    
#funcion principal     
# una instancia de la ventana     
window = Tk() 
window.geometry("980x700")
window.title("Trolebus")
canvas = Canvas( window, bg = "#FFFFFF", height = 700, width = 980 )
canvas.place(x = 0, y = 0)
pantallaInicio()
botones()
menudesplegable()
window.mainloop()

