const net = require('net');
const readline = require('readline');

// Crear interfaz para la entrada y salida
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

// Solicitar IP y puerto del servidor
rl.question('Ingrese la dirección IP del servidor: ', (host) => {
    rl.question('Ingrese el puerto del servidor: ', (port) => {
        const client = new net.Socket();

        // Conectar al servidor
        client.connect(port, host, () => {
            console.log('Conectado al servidor.');

            rl.question('Ingrese su nombre: ', (name) => {
                client.write(name);
                startChat(client);
            });
        });

        client.on('data', (data) => {
            console.log(data.toString());
        });

        client.on('error', (err) => {
            console.error('Error de conexión:', err.message);
        });

        client.on('close', () => {
            console.log('Conexión cerrada.');
            rl.close();
        });
    });
});

// Función para iniciar el chat
function startChat(client) {
    rl.on('line', (input) => {
        if (input === '/quitar') {
            client.write(input);
            client.destroy(); // Cierra la conexión
        } else if (input === '/listar') {
            client.write(input);
        } else {
            client.write(input);
        }
    });
}
