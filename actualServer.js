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
    const messageString = message.toString();
    console.log(messageString)
    console.log(senderInfo)
    
    if (messageString === 'create a game room') {
        setTimeout(() => {
            console.log("Timeout reached. Sending 'Start' message.");
            broadcastStart('Start');
            startMessageSent = true;
        }, 8000);
    }

    else if (messageString.endsWith(':ready')) {
        // Check if the client's address is already in the list
        const playerName = messageString.split(":")[1]
        if (messageString.startsWith('O')){
            const clientOculusExists = clientsOculus.some(client => 
                client.address === senderInfo.address && client.port === senderInfo.port
            );
    
            if (!clientOculusExists) {
                // If the client is not in the list, add information about the client
                clientsOculus.push({
                    playerName: playerName,
                    address: senderInfo.address,
                    port: senderInfo.port
                });
    
                //console.log("Updated clients array:", clientsOculus);
                console.log(`Oculus Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
                
                // Send an acknowledgment back to the client
                // server.send('ack', senderInfo.port, senderInfo.address, () => {
                //     console.log(`Acknowledgment sent to oculus ${senderInfo.address}:${senderInfo.port}`);
                // });
                
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
                    playerName: playerName,
                    address: senderInfo.address,
                    port: senderInfo.port
                });
    
                console.log("Updated clients array:", clientsRasp);
                console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
                
                // Send an acknowledgment back to the client
                // server.send('ack', senderInfo.port, senderInfo.address, () => {
                //     console.log(`Acknowledgment sent to rasp ${senderInfo.address}:${senderInfo.port}`);
                // });
                
            } else {
                console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
                //server.send('ha ha', senderInfo.port, senderInfo.address)
            }
        }
    } 
    else if (messageString === 'disconnect') {
        const indexOculus = clientsOculus.findIndex(client => client.address === senderInfo.address && client.port === senderInfo.port);
        const indexRasp = clientsRasp.findIndex(client => client.address === senderInfo.address && client.port === senderInfo.port);

        if (indexOculus !== -1) {
            clientsOculus.splice(indexOculus, 1);
            console.log(`Oculus Client at ${senderInfo.address}:${senderInfo.port} disconnected.`);
        } else if (indexRasp !== -1) {
            clientsRasp.splice(indexRasp, 1);
            console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} disconnected.`);
        }
    }
    else {
        
        if (startMessageSent && checkAllClientsConnected()) {
            const [messageType, playerName, sequenceNum, charOne, charTwo] = messageString.split(":");
            if (messageType === 'O'){
                broadcast(message)
                //send message to the client with same playerName but messageType is "R"
                const matchingRaspClient = clientsRasp.find(client => client.playerName === playerName);
                if (matchingRaspClient) {
                    // Send the message to the matching Rasp client
                    server.send(message, matchingRaspClient.port, matchingRaspClient.address, (error) => {
                        if (error) {
                            console.error(`Error sending message to Rasp client ${matchingRaspClient.address}:${matchingRaspClient.port}: ${error.message}`);
                        } else {
                            console.log(`Message sent to Rasp client ${matchingRaspClient.address}:${matchingRaspClient.port}`);
                        }
                    });
                } else {
                    console.log(`No matching Rasp client found for ${playerName}`);
                }
            }
            else if (messageType === 'R'){
                //send message to the client with same playerName but messageType is "O"
                //console.log("broadcasting")
                //broadcast(message)
                const matchingOculusClient = clientsOculus.find(client => client.playerName === playerName);
                if (matchingOculusClient) {
                    // Send the message to the matching Oculus client
                    server.send(message, matchingOculusClient.port, matchingOculusClient.address, (error) => {
                        if (error) {
                            console.error(`Error sending message to Oculus client ${matchingOculusClient.address}:${matchingOculusClient.port}: ${error.message}`);
                        } else {
                            console.log(`Message sent to Oculus client ${matchingOculusClient.address}:${matchingOculusClient.port}`);
                        }
                    });
                } else {
                    console.log(`No matching Oculus client found for ${playerName}`);
                }
            }

            console.log(`Message received from ${senderInfo.address}:${senderInfo.port}: ${messageString}`);
            
        }
    }
});

function broadcast(message) {
    clientsOculus.forEach((client) => {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } else {
                console.log(`Message broadcasted to ${client.address}:${client.port}`);
            }
        });
    });
    //added for now: testing
    clientsRasp.forEach((client) => {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } else {
                console.log(`Message broadcasted to ${client.address}:${client.port}`);
            }
        });
    });
}

function broadcastStart(message) {
    clientsRasp.forEach((client) => {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } else {
                console.log(`Start Message broadcasted to ${client.address}:${client.port}`);
            }
        });
    });
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
    //return clientsRasp.length >= 1;
}

server.bind(5500);
