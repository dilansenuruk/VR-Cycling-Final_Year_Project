const { error } = require('console');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const clients = [];
let sequenceNumber = 1; // Initialize the sequence number

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
    console.log(senderInfo)
    //console.log(messageString)

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
	    const ack_msg = `0:ack`
            server.send(ack_msg, senderInfo.port, senderInfo.address, () => {
		
                console.log(`Acknowledgment sent to ${senderInfo.address}:${senderInfo.port}`);
            });
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
        // If the message is not 'ready', extract the sequence number and broadcast the message
        const [receivedSequenceNumber, command] = messageString.split(':');
	console.log(receivedSequenceNumber)
        
        console.log(`Message received from ${senderInfo.address}:${senderInfo.port} with sequence number ${receivedSequenceNumber}: ${command}`);
        broadcast(message, senderInfo, receivedSequenceNumber);
    }
});

function broadcast(message, senderInfo, receivedSequenceNumber) {
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
            // Send a discard message with the received sequence number to the sender
            const discardMessage = `${receivedSequenceNumber}:discard`;
            
            server.send(discardMessage, senderInfo.port, senderInfo.address, () =>{
                console.log(`Discard message sent to ${senderInfo.address}:${senderInfo.port}`);
		console.log(discardMessage);
            });
        }
    });
}

server.bind(5500);
