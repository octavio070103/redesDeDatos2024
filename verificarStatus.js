const fs = require('fs');//Módulo que permite interactuar con el sistema de archivos, en este caso para leer archivos.
//Módulos que permiten realizar solicitudes HTTP y HTTPS.
const http = require('http');
const https = require('https');

// Esta funcio realiza una solicitud HTTP a la URL proporcionada y devuelve el estado de la respuesta (código y mensaje).
function getHttpStatus(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        const request = client.get(url, (res) => {
            resolve(`${res.statusCode} ${res.statusMessage}`);
        });
        
        request.on('error', (err) => {
            reject(err.message);
        });

        // Timeout para la solicitud
        request.setTimeout(5000, () => { // 5 segundos
            request.abort(); // Aborta la solicitud
            reject('Timeout de la solicitud');
        });
    });
}

// esta Funcion obtiene información de geolocalización para una dirección IP utilizando la API ip-api.com.
async function getGeolocation(ip) {
    return new Promise((resolve, reject) => {
        http.get(`http://ip-api.com/json/${ip}`, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                const info = JSON.parse(data);
                resolve(info);
            });
        }).on('error', (err) => {
            reject(err.message);
        });
    });
}

// Función Lee y procesa el archivo (file) que contiene URLs, realiza solicitudes HTTP para cada una y obtiene su estado, así como la geolocalización de su IP.
async function checkUrls(file) {
    try {
        const data = fs.readFileSync(file, 'utf8');
        const urls = data.split('\n').filter(Boolean); // Filtrar líneas vacías
        const results = [];

        for (const url of urls) {
            try {
                const status = await getHttpStatus(url);
                results.push(`${url}: ${status}`);
                
                // Agregar geolocalización
                const ipMatch = url.match(/\/\/([^\/]+)/);
                if (ipMatch && ipMatch[1]) {
                    const geolocation = await getGeolocation(ipMatch[1]);
                    results.push(`Geolocalización de -> ${ipMatch[1]}: ${JSON.stringify(geolocation)}`);
                }
            } catch (error) {
                results.push(`${url}: ${error}`);
            }

            // Agregar separador después de cada resultado
            results.push('-----------------------------------------------------------');
        }

        console.log('\nResultados de las solicitudes HTTP:');
        results.forEach(result => console.log(result));
    } catch (error) {
        console.error('Error al leer el archivo:', error);
    }
}


// Ejecutar el chequeo de URLs
checkUrls('urls.txt');//urls.txt contiene las urls a verificar 