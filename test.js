const { error } = require('console');
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
                broadcast('Start');
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

    } else {
        // If the message is not 'ready', broadcast it to all connected clients
        console.log(`Message received from ${senderInfo.address}:${senderInfo.port}: ${messageString}`);
        broadcast(message, senderInfo);
    }
});

function broadcast(message, senderInfo) {
    // Broadcast the message to all connected clients except the sender. Send a discard message to the sender
    clients.forEach((client) => {
        if (client.address !== senderInfo.address || client.port !== senderInfo.port) {
            server.send(message, client.port, client.address, (error) => {
                if (error) {
                    console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
                } else {
                    console.log(`Message broadcasted to ${client.address}:${client.port}`);
                }
            });
        } else {
            server.send(message, senderInfo.port, senderInfo.address, () =>{
                console.log(`Discard message sent to ${senderInfo.address}:${senderInfo.port}`);
            })
        }
    });
}

function checkAllClientsConnected() {
    // Check if all expected clients have connected
    // Modify this function according to your logic for determining all clients connected
    // In this example, it checks if there are at least 2 clients connected (change it according to your requirement)
    return clients.length >= 2;
}

server.bind(5500);
