const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const clients = [];
let startMessageSent = false;

server.on('error', (error) => {
    console.log('Error on the server \n' + error.message);
    server.close();
});

server.on('listening', () => {
    const address = server.address();
    console.log(`Server is listening on ${address.address}:${address.port}`);

    // Wait for 5 seconds before checking if all clients have connected
    setTimeout(() => {
        if (!startMessageSent) {
            console.log("Timeout reached. Closing server.");
            server.close();
        }
    }, 5000);
});

server.on('message', (message, senderInfo) => {
    const messageString = message.toString();
    console.log(senderInfo)

    if (messageString === 'ready') {
        // Check if the client's address is already in the list
        const clientExists = clients.some(client => 
            client.address === senderInfo.address && client.port === senderInfo.port
        );

        if (!clientExists) {
            // If the client is not in the list, add information about the client
            clients.push({
                address: senderInfo.address,
                port: senderInfo.port
            });

            console.log("Updated clients array:", clients);
            console.log(`Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
            
            // Send an acknowledgment back to the client
            server.send('ack', senderInfo.port, senderInfo.address, () => {
                console.log(`Acknowledgment sent to ${senderInfo.address}:${senderInfo.port}`);
            });

            // If all clients are connected, send the start message
            if (!startMessageSent && checkAllClientsConnected()) {
                startMessageSent = true;
                console.log("All clients connected. Sending 'Start' message.");

                // Start broadcasting messages in a separate Worker Thread
                const broadcastWorker = new Worker('./broadcastWorker.js', {
                    workerData: { message, senderInfo, clients }
                });

                broadcastWorker.on('message', (result) => {
                    console.log(`Broadcasting completed: ${result}`);
                });

                broadcastWorker.on('error', (error) => {
                    console.error('Broadcasting error:', error);
                });

                broadcastWorker.on('exit', (code) => {
                    if (code !== 0) {
                        console.error(`Broadcasting worker stopped with exit code ${code}`);
                    }
                });
            }
        } else {
            console.log(`Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
        }
    } else if(messageString === 'disconnect'){
        const index = clients.findIndex(client => client.address === senderInfo.address && client.port === senderInfo.port);
        if (index !== -1) {
            clients.splice(index, 1);
            console.log(`Client at ${senderInfo.address}:${senderInfo.port} disconnected.`);
        }
    }
});

function checkAllClientsConnected() {
    return clients.length >= 1;
}

server.bind(5500);
