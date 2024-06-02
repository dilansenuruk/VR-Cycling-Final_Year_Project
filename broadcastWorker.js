const { parentPort, workerData } = require('worker_threads');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const { message, senderInfo, clients } = workerData;
console.log("msg broadcasting from the server",workerData)
console.log("test--------------");
const messageString = Buffer.from(message).toString('utf-8');
console.log("test",messageString);

// Broadcast the message to all connected clients except the sender
console.log("client data  -----------------------", clients);
clients.forEach((client) => {
    if (client.address !== senderInfo.address || client.port !== senderInfo.port) {
        // server.send("bitch",client.port, client.address)
        server.send(messageString, client.port, client.address, (error) => {
            if (error) {
                console.log("error --------",error);
                parentPort.postMessage(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } 
            else {
                parentPort.postMessage(`Message broadcasted to ${client.address}:${client.port}`);
                // parentPort.postMessage('Broadcasting completed.');
            }
        });
    } else {
            console.log("msg--",messageString);
            server.send(messageString, senderInfo.port, senderInfo.address, () =>{
            parentPort.postMessage(`Discard message(${messageString}) sent to ${senderInfo.address}:${senderInfo.port}`);
        })
    }
});

