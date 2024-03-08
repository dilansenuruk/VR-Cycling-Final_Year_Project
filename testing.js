const { error } = require('console');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const clients = [];

server.on('error', (error) => {
    console.log('Error on the server \n' + error.message);
    server.close();
});

server.on('listening', () => {
    const address = server.address();
    console.log(`Server is listening on ${address.address}:${address.port}`);
});

server.on('message', (message, senderInfo) => {
    const messageString = message.toString();
    const messageType = messageString.split(':')[0]; // Extract the message type (o or r)

    if (messageType === 'o' || messageType === 'r') {
        const id = messageString.split(':')[1];

        if (messageString.endsWith(':ready')) {
            // Ready message
            const clientExists = clients.some(client => 
                client.address === senderInfo.address && client.port === senderInfo.port && client.type === messageType && client.id === id
            );

            if (!clientExists) {
                // If the client is not in the list, add information about the client
                clients.push({
                    address: senderInfo.address,
                    port: senderInfo.port,
                    type: messageType,
                    id: id
                });
                console.log("Updated clients array:", clients);
            } 

            // Send an acknowledgment back to the client
            server.send('ack', senderInfo.port, senderInfo.address, () => {
                console.log(`Acknowledgment sent to ${senderInfo.address}:${senderInfo.port}`);
            });
        } else if (messageType === 'o') {
            // Resistance time message from Oculus to Raspberry Pi
            const recipient = clients.find(client => client.type === 'r' && client.id === id);
            if (recipient) {
                server.send(message, recipient.port, recipient.address, (error) => {
                    if (error) {
                        console.error(`Error sending to ${recipient.address}:${recipient.port}: ${error.message}`);
                    } else {
                        console.log(`Message sent to ${recipient.address}:${recipient.port}`);
                    }
                });
            }
        } else if (messageType === 'r') {
            // Speed and distance message from Raspberry Pi to all Raspberry Pis
            clients.forEach((client) => {
                if (client.type === 'r' && client.id !== id) {
                    server.send(message, client.port, client.address, (error) => {
                        if (error) {
                            console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
                        } else {
                            console.log(`Message broadcasted to ${client.address}:${client.port}`);
                        }
                    });
                }
            });
        }
    } else {
        // Invalid message type
        console.log(`Invalid message type: ${messageType}`);
    }
});

server.bind(5500);
