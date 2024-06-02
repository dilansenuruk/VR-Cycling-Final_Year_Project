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
    
});

server.on('message', (message, senderInfo) => {
    console.log("msg received to the server", message)
    const messageString = message.toString();
    console.log(senderInfo)
    
    if (messageString === 'create a game room') {
        setTimeout(() => {
            console.log("Timeout reached. Sending 'Start' message.");
            broadcast('Start');
            startMessageSent = true;
        }, 8000);
    }

    else if (messageString === 'ready') {
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
            
        } else {
            console.log(`Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
            server.send('ha ha', senderInfo.port, senderInfo.address)
        }
    } else if(messageString === 'disconnect'){
        const index = clients.findIndex(client => client.address === senderInfo.address && client.port === senderInfo.port);
        if (index !== -1) {
            clients.splice(index, 1);
            console.log(`Client at ${senderInfo.address}:${senderInfo.port} disconnected.`);
        }
    }
    else {
        console.log(`Message received from ${senderInfo.address}:${senderInfo.port}: ${messageString}`);
        if (startMessageSent && checkAllClientsConnected()) {
            // Start broadcasting messages in a separate Worker Thread
            const broadcastWorker = new Worker('./broadcastWorker.js', {
                workerData: { message: Buffer.from(message), senderInfo, clients }
            });

            broadcastWorker.on('message', (result) => {
                console.log(`Broadcasting completed: ${result}`);
                server.send(result, )
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
    }
});

function broadcast(message) {
    clients.forEach((client) => {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } else {
                console.log(`Start Message broadcasted to ${client.address}:${client.port}`);
            }
        });
    });
}

function checkAllClientsConnected() {
    return clients.length >= 1;
}

server.bind(5500);
