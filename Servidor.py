import socket  # Importa el módulo 'socket' para la comunicación por socket.
import threading  # Importa el módulo 'threading' para trabajar con hilos.

# Diccionario para mantener un registro de los clientes conectados
clientes_conectados = {}

# Semáforo para sincronizar el acceso a los clientes conectados
sem = threading.Semaphore()

# Configuración del servidor
host = '127.0.0.1'  # Define la dirección IP en la que el servidor escuchará conexiones.
puerto = 50123  # Define el número de puerto en el que el servidor escuchará conexiones.

# Crea un socket de tipo AF_INET (IPv4) y SOCK_STREAM (TCP).
socketServidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Asocia el socket con la dirección y el puerto especificados.
socketServidor.bind((host, puerto))

# Comienza a escuchar conexiones entrantes.
socketServidor.listen()

# Función para enviar mensajes a todos los clientes, excepto el origen
def broadcast(origen, mensaje):
    for cliente_socket in clientes_conectados:
        if cliente_socket != origen:
            try:
                cliente_socket.send(mensaje.encode())  # Envía el mensaje codificado a cada cliente.
            except ConnectionError:
                # Manejar desconexiones inesperadas eliminando el cliente del registro.
                cliente_a_eliminar = clientes_conectados.pop(cliente_socket, None)
                if cliente_a_eliminar:
                    print(f"Cliente {cliente_a_eliminar} desconectado inesperadamente.")

def manejar_cliente(socketConexion, nombre_cliente):
    try:
        # Añade el nuevo cliente a la lista de conectados
        clientes_conectados[socketConexion] = nombre_cliente

        while True:
            mensajeRecibido = socketConexion.recv(1024).decode()  # Recibe un mensaje del cliente y lo decodifica.

            if mensajeRecibido.startswith('/listar'):
                # Si el mensaje comienza con '/listar', se genera una lista de nombres de clientes y se envía.
                lista_usuarios = "USUARIOS CONECTADOS:\n"
                for idx, nombre in enumerate(clientes_conectados.values(), 1):
                    lista_usuarios += f"usuario {idx}: {nombre}\n"

                socketConexion.send(lista_usuarios.encode())

            elif mensajeRecibido == '/quitar':
                # Si el mensaje es '/quitar', se sale del bucle, lo que permite desconectar al cliente.
                break

            else:
                # Si el mensaje no es un comando especial, se prepara el mensaje a enviar.
                mensaje_enviar = f"{nombre_cliente}: {mensajeRecibido}"
                
                # Usa semáforos para sincronizar la transmisión de mensajes
                sem.acquire()
                broadcast(socketConexion, mensaje_enviar)  # Llama a la función para enviar el mensaje a todos
                sem.release()

    except ConnectionResetError:
        pass
    finally:
        # Finaliza cuando el cliente se desconecta y realiza limpieza.
        print(f"Desconectado el cliente {nombre_cliente}")
        socketConexion.close()  # Cierra la conexión del cliente.
        sem.acquire()
        del clientes_conectados[socketConexion]  # Elimina al cliente del registro.
        sem.release()

while True:
    socketConexion, addr = socketServidor.accept()  # Acepta una nueva conexión entrante.
    print("Conectado con un cliente", addr)  # Muestra la información de la conexión entrante.

    nombre_cliente = socketConexion.recv(1024).decode()  # Recibe el nombre del cliente que se ha unido.
    print(f"Cliente {nombre_cliente} se ha unido.")

    clientes_conectados[socketConexion] = nombre_cliente  # Agrega al cliente al registro de clientes conectados.

    # Inicia un hilo para manejar al cliente y pasa la conexión y el nombre del cliente como argumentos.
    cliente_thread = threading.Thread(target=manejar_cliente, args=(socketConexion, nombre_cliente))
    cliente_thread.start()

    # Muestra la lista de nombres de los clientes conectados.
    print("Clientes conectados:", list(clientes_conectados.values()))
