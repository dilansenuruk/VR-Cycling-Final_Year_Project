const { error } = require('console');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');

const clientsOculus = [];
const clientsRasp = [];
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

    else if (messageString.endsWith(':ready')) {
        // Check if the client's address is already in the list
        if (messageString.startsWith('O')){
            const clientOculusExists = clientsOculus.some(client => 
                client.address === senderInfo.address && client.port === senderInfo.port
            );
    
            if (!clientOculusExists) {
                // If the client is not in the list, add information about the client
                clientsOculus.push({
                    address: senderInfo.address,
                    port: senderInfo.port
                });
    
                console.log("Updated clients array:", clientsOculus);
                console.log(`Oculus Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
                
                // Send an acknowledgment back to the client
                server.send('ack', senderInfo.port, senderInfo.address, () => {
                    console.log(`Acknowledgment sent to oculus ${senderInfo.address}:${senderInfo.port}`);
                });
                
            } else {
                console.log(`Oculus Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
                //server.send('ha ha', senderInfo.port, senderInfo.address)
            }
        }
        
        if (messageString.startsWith('R')){
            const clientRaspExists = clientsRasp.some(client => 
                client.address === senderInfo.address && client.port === senderInfo.port
            );
    
            if (!clientRaspExists) {
                // If the client is not in the list, add information about the client
                clientsRasp.push({
                    address: senderInfo.address,
                    port: senderInfo.port
                });
    
                console.log("Updated clients array:", clientsRasp);
                console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
                
                // Send an acknowledgment back to the client
                server.send('ack', senderInfo.port, senderInfo.address, () => {
                    console.log(`Acknowledgment sent to rasp ${senderInfo.address}:${senderInfo.port}`);
                });
                
            } else {
                console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
                //server.send('ha ha', senderInfo.port, senderInfo.address)
            }
        }
        
    } else if(messageString === 'disconnect'){
        const index = clients.findIndex(client => client.address === senderInfo.address && client.port === senderInfo.port);
        if (index !== -1) {
            clients.splice(index, 1);
            console.log(`Client at ${senderInfo.address}:${senderInfo.port} disconnected.`);
        }
    }
    else {
        
        if (startMessageSent && checkAllClientsConnected()) {
            const [messageType, playerName, sequenceNum, charOne, charTwo] = messageString.split(":");
            if (messageType === 'O'){
                broadcast(message)
                //send message to the client with same playerName but messageType is "R"
            }
            if (messageType === 'R'){
                //send message to the client with same playerName but messageType is "O"
            }

            console.log(`Message received from ${senderInfo.address}:${senderInfo.port}: ${messageString}`);
            //broadcasting messages
            //broadcast(message)
        }
    }
});

function broadcast(message) {
    clientsOculus.forEach((client) => {
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
    return clientsOculus.length >= 1;
}

server.bind(5500);
