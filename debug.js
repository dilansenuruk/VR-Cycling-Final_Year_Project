const { parentPort, workerData } = require('worker_threads');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const { message, senderInfo, clients } = workerData;
// console.log("msg broadcasting from the server",workerData)
// message = Buffer.from(message)
// const messageString = Buffer.from(message).toString('utf-8');
// console.log("test",messageString);

// Broadcast the message to all connected clients except the sender
console.log(message)
const messageBuffer = Buffer.from(message)
console.log(messageBuffer)
clients.forEach((client) => {
    if (client.address !== senderInfo.address || client.port !== senderInfo.port) {
        server.send(messageBuffer, client.port, client.address, (error) => {
            if (error) {
                parentPort.postMessage(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } 
            else {
                parentPort.postMessage(`Message broadcasted to ${client.address}:${client.port}`);
            }
        });
    } else {
            server.send(messageBuffer, senderInfo.port, senderInfo.address, () =>{
            parentPort.postMessage(`Discard message sent to ${senderInfo.address}:${senderInfo.port}`);
        })
    }
});

parentPort.postMessage('Broadcasting completed.');
