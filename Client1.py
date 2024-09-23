import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Función para recibir mensajes del servidor
def recibir_mensajes(socket):
    while True:
        try:
            mensaje = socket.recv(1024).decode()
            if not mensaje:
                break

            texto_chat.config(state=tk.NORMAL)
            texto_chat.insert(tk.END, mensaje + '\n')
            texto_chat.config(state=tk.DISABLED)
            texto_chat.yview(tk.END)
        except ConnectionError:
            messagebox.showerror("Error", "Se ha perdido la conexión con el servidor.")
            break

# Función para enviar mensajes al servidor
def enviar_mensaje(event=None):
    mensaje = entrada_mensaje.get()
    if mensaje:
        texto_chat.config(state=tk.NORMAL)
        texto_chat.insert(tk.END, f"Tú: {mensaje}\n")
        texto_chat.config(state=tk.DISABLED)
        texto_chat.yview(tk.END)

        if mensaje == '/quitar':
            cliente.send(mensaje.encode())
            ventana_chat.quit()
        elif mensaje == '/listar':
            cliente.send(mensaje.encode())
        else:
            cliente.send(mensaje.encode())

        entrada_mensaje.delete(0, tk.END)

# Función para cerrar la conexión y la ventana
def cerrar_conexion():
    cliente.send('/quitar'.encode())
    cliente.close()
    ventana_chat.quit()

# Configuración del cliente
host = '127.0.0.1'
puerto = 50123

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((host, puerto))

# Función para iniciar la interfaz gráfica
def iniciar_interfaz():
    global ventana_chat, entrada_mensaje, texto_chat

    ventana_chat = tk.Tk()
    ventana_chat.title("Chat Cliente")

    texto_chat = scrolledtext.ScrolledText(ventana_chat, wrap=tk.WORD, state=tk.DISABLED, width=50, height=20)
    texto_chat.grid(column=0, row=0, padx=10, pady=10, columnspan=2)

    entrada_mensaje = tk.Entry(ventana_chat, width=40)
    entrada_mensaje.grid(column=0, row=1, padx=10, pady=10)
    entrada_mensaje.bind("<Return>", enviar_mensaje)  # Envía mensaje al presionar Enter

    boton_enviar = tk.Button(ventana_chat, text="Enviar", width=10, command=enviar_mensaje)
    boton_enviar.grid(column=1, row=1, padx=10, pady=10)

    boton_quitar = tk.Button(ventana_chat, text="salir", width=10, command=cerrar_conexion)
    boton_quitar.grid(column=1, row=2, padx=10, pady=10)

    ventana_chat.protocol("WM_DELETE_WINDOW", cerrar_conexion)

    ventana_chat.mainloop()

# Solicita el nombre del usuario
def pedir_nombre():
    ventana_nombre = tk.Tk()
    ventana_nombre.title("Ingresa tu nombre")

    etiqueta_nombre = tk.Label(ventana_nombre, text="Ingresa tu nombre:")
    etiqueta_nombre.pack(pady=10)

    entrada_nombre = tk.Entry(ventana_nombre, width=40)  # Aumentar el tamaño
    entrada_nombre.pack(pady=10)

    def enviar_nombre(event=None):
        nombre = entrada_nombre.get()
        if nombre:
            cliente.send(nombre.encode())
            ventana_nombre.destroy()
        else:
            messagebox.showwarning("Advertencia", "El nombre no puede estar vacío.")

    entrada_nombre.bind("<Return>", enviar_nombre)  # Enviar con Enter

    boton_enviar_nombre = tk.Button(ventana_nombre, text="Enviar", command=enviar_nombre)
    boton_enviar_nombre.pack(pady=10)

    # Centrar la ventana
    ventana_nombre.update_idletasks()  # Actualiza el tamaño de la ventana
    x = (ventana_nombre.winfo_screenwidth() // 2) - (ventana_nombre.winfo_width() // 2)
    y = (ventana_nombre.winfo_screenheight() // 2) - (ventana_nombre.winfo_height() // 2)
    ventana_nombre.geometry(f"+{x}+{y}")  # Posicionar en el centro

    ventana_nombre.mainloop()

# Hilo para recibir mensajes
thread_recv = threading.Thread(target=recibir_mensajes, args=(cliente,))
thread_recv.daemon = True
thread_recv.start()

# Inicia el flujo del programa
pedir_nombre()
iniciar_interfaz()

cliente.close()
