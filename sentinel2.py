from tkinter import *
from tkinter import messagebox
import sqlite3
import re




def conexionBBDD():

    miConexion=sqlite3.connect("Usuarios")
    miCursor=miConexion.cursor()

    try:
        miCursor.execute('''
        CREATE TABLE DATOSUSUARIOS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        NOMBRE_USUARIO VARCHAR(50),
        PASSWORD VARCHAR(50),
        APELLIDO VARCHAR(10),
        DIRECCION VARCHAR(50),
        COMENTARIOS VARCHAR(100))
        ''')
        messagebox.showinfo("BBDD","BBDD CREADA CON EXITO")
    except:
    
        messagebox.showwarning("¡Atención!", "La BBDD ya existe")
    


def salirAplicacion():
    valor=messagebox.askquestion("Salir", "¿Deseas salir de la aplicación?")

    if valor=="yes":
        root.destroy()
    

def limpiarCampos():
    miId.set("")
    miNombre.set("")
    miApellido.set("")
    miDireccion.set("")
    miPass.set("")
    textoComentario.delete(1.0, END)



def crear():
    
    miConexion=sqlite3.connect("Usuarios")
    miCursor=miConexion.cursor()

    if validarPassword(miPass.get()) == False:
        miConexion.commit()
        messagebox.showwarning("Atención", "La contraseña no cumple las politicas de seguridad")
    else:
        datos_usuario=miNombre.get(),miPass.get(),miApellido.get(),miDireccion.get(),textoComentario.get("1.0",END)
        miCursor.execute("INSERT INTO DATOSUSUARIOS VALUES(NULL,?,?,?,?,?)",(datos_usuario))

        miConexion.commit()
        messagebox.showinfo("BBDD", "Registro insertado con exito")


    


    """miCursor.execute("INSERT INTO DATOSUSUARIOS VALUES(NULL,'"
    +miNombre.get()+"','" 
    +miPass.get()+"','" 
    +miApellido.get()+"','" 
    +miDireccion.get()+"','" 
    +textoComentario.get("1.0",END)+"')")"""
    
   




def leer():
    miConexion=sqlite3.connect("Usuarios")
    miCursor=miConexion.cursor()

    miCursor.execute("SELECT * FROM DATOSUSUARIOS WHERE ID=" + miId.get())

    elUsuario=miCursor.fetchall()

    for usuario in elUsuario:
        miId.set(usuario[0])
        miNombre.set(usuario[1])
        miPass.set(usuario[2])
        miApellido.set(usuario[3])
        miDireccion.set(usuario[4])
        textoComentario.insert(1.0, usuario[5])

    miConexion.commit()
    
def actualizar():
    miConexion=sqlite3.connect("Usuarios")
    miCursor=miConexion.cursor()

    datos_usuario=miNombre.get(),miPass.get(),miApellido.get(),miDireccion.get(),textoComentario.get("1.0",END)
    miCursor.execute("UPDATE DATOSUSUARIOS SET NOMBRE_USUARIO=?,PASSWORD=?,APELLIDO=?,DIRECCION=?,COMENTARIOS=? WHERE ID="+miId.get(),(datos_usuario))

    """miCursor.execute("UPDATE DATOSUSUARIOS SET NOMBRE_USUARIO='"
    +miNombre.get()+"',PASSWORD='" 
    +miPass.get()+"',APELLIDO='" 
    +miApellido.get()+"',DIRECCION='" 
    +miDireccion.get()+"',COMENTARIOS='" 
    +textoComentario.get("1.0",END)+"' WHERE ID=" + miId.get())"""
    
    miConexion.commit()
    messagebox.showinfo("BBDD", "Registro actualizado con exito")


def eliminar():
    miConexion=sqlite3.connect("Usuarios")
    miCursor=miConexion.cursor()

    miCursor.execute("DELETE FROM DATOSUSUARIOS WHERE ID=" + miId.get())
    
    miConexion.commit()
    messagebox.showinfo("BBDD", "Registro eliminado con exito")


def validarPassword(password):
    
    if 8<= len(password) <=16:
        if re.search('[a-z]',password) and re.search('[A-Z]',password) and re.search('[0-9]',password):
            result = TRUE
    else:
        result = FALSE
    return result


def autor():
    messagebox.showinfo("APP_AGA", "Aplicación desarrollada por AGA")




root=Tk()

##Construccion de barra de Menu###
barraMenu=Menu(root)
root.config(menu=barraMenu, width=300, height=300)

##Opciones de la barra de Menu
bbddMenu=Menu(barraMenu, tearoff=0)
bbddMenu.add_command(label="Conectar",command=conexionBBDD)
bbddMenu.add_command(label="Salir",command=salirAplicacion)

borrarMenu=Menu(barraMenu, tearoff=0)
borrarMenu.add_command(label="Borrar campos", command=limpiarCampos)

crudMenu=Menu(barraMenu, tearoff=0)
crudMenu.add_command(label="Crear", command=crear)
crudMenu.add_command(label="Leer", command=leer)
crudMenu.add_command(label="Actualizar",command=actualizar)
crudMenu.add_command(label="Borrar",command=eliminar)

ayudaMenu=Menu(barraMenu, tearoff=0)
ayudaMenu.add_command(label="Licencia", command=autor)
ayudaMenu.add_command(label="Acerca de...")

barraMenu.add_cascade(label="BBDD", menu=bbddMenu)
barraMenu.add_cascade(label="Borrar", menu=borrarMenu)
barraMenu.add_cascade(label="Crud", menu=crudMenu)
barraMenu.add_cascade(label="Ayuda", menu=ayudaMenu)

##########Frame1#######################
miFrame=Frame(root)
miFrame.pack()

################TextBox#################

#######StringVar()#######Permite rescatar los textos en BBDD
miId=StringVar()
miNombre=StringVar()
miApellido=StringVar()
miPass=StringVar()
miDireccion=StringVar()


cuadroID=Entry(miFrame, textvariable=miId)
cuadroID.grid(row=0,column=1,padx=10,pady=10)

cuadroNombre=Entry(miFrame, textvariable=miNombre)
cuadroNombre.grid(row=1,column=1,padx=10,pady=10)
cuadroNombre.config(fg="red", justify="right")

cuadroPass=Entry(miFrame, textvariable=miPass)
cuadroPass.grid(row=2,column=1,padx=10,pady=10)
cuadroPass.config(show="*")

cuadroApellido=Entry(miFrame,textvariable=miApellido)
cuadroApellido.grid(row=3,column=1,padx=10,pady=10)

cuadroDireccion=Entry(miFrame, textvariable=miDireccion)
cuadroDireccion.grid(row=4,column=1,padx=10,pady=10)

textoComentario=Text(miFrame, width=16, height=5)
textoComentario.grid(row=5,column=1,padx=10,pady=10)
scrollVert=Scrollbar(miFrame, command=textoComentario.yview)
scrollVert.grid(row=5,column=2, sticky="nsew")

textoComentario.config(yscrollcommand=scrollVert.set)

###############label################################

idLabel=Label(miFrame, text="Id:")
idLabel.grid(row=0,column=0,sticky="e",padx=10,pady=10)

idLabel=Label(miFrame, text="Nombre:")
idLabel.grid(row=1,column=0,sticky="e",padx=10,pady=10)

idLabel=Label(miFrame, text="Password:")
idLabel.grid(row=2,column=0,sticky="e",padx=10,pady=10)

idLabel=Label(miFrame, text="Apellido:")
idLabel.grid(row=3,column=0,sticky="e",padx=10,pady=10)

idLabel=Label(miFrame, text="Direccion:")
idLabel.grid(row=4,column=0,sticky="e",padx=10,pady=10)

idLabel=Label(miFrame, text="Comentarios:")
idLabel.grid(row=5,column=0,sticky="e",padx=10,pady=10)


########Frame2###########################################
miFrame2=Frame(root)
miFrame2.pack()

###############Boton#####################################

botonCrear=Button(miFrame2, text="Create", command=crear)
botonCrear.grid(row=1,column=0, sticky="e",padx=10,pady=10)

botonLeer=Button(miFrame2, text="Read", command=leer)
botonLeer.grid(row=1,column=1, sticky="e",padx=10,pady=10)

botonActualizar=Button(miFrame2, text="Update",command=actualizar)
botonActualizar.grid(row=1,column=2, sticky="e",padx=10,pady=10)

botonBorrar=Button(miFrame2, text="Delete",command=eliminar)
botonBorrar.grid(row=1,column=3, sticky="e",padx=10,pady=10)



root.mainloop()