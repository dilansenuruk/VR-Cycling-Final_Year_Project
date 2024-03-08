const { parentPort, workerData } = require('worker_threads');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const { message, senderInfo, clients } = workerData;

// Broadcast the message to all connected clients except the sender
clients.forEach((client) => {
    if (client.address !== senderInfo.address || client.port !== senderInfo.port) {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                parentPort.postMessage(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } else {
                parentPort.postMessage(`Message broadcasted to ${client.address}:${client.port}`);
            }
        });
    } else {
        server.send(message, senderInfo.port, senderInfo.address, () =>{
            parentPort.postMessage(`Discard message sent to ${senderInfo.address}:${senderInfo.port}`);
        })
    }
});

parentPort.postMessage('Broadcasting completed.');
