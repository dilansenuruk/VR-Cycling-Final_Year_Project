const { error } = require('console');
const dgram = require('dgram');
const server = dgram.createSocket('udp4');
const os = require('os');
const numCPUs = os.cpus().length;
console.log(`Number of CPU cores: ${numCPUs}`);

const clientsOculus = [];
const clientsRasp = [];
let startMessageSent = false;
let noOfPlayers

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


    if(messageString.startsWith('no_players')){
        noOfPlayers = messageString;
        
        //broadcast(messageString);
    }
    
    else if (messageString === 'create a game room') {
        broadcastRpi('game created');
        console.log(clientsRasp)
        // setTimeout(() => {
        //     clientsOculus.length = 0;
        //     clientsRasp.length = 0;
                
            
            
        // }, 2000);
        // clear the arrays clientsOculus and clientRasp

        
        
        setTimeout(() => {
            console.log("Timeout reached. Sending 'Start' message.");
            
            console.log("player names sent")
            setTimeout(() => {
                
                broadcastStart('Start');
                
                startMessageSent = true;
            }, 2000);
            broadcast(noOfPlayers);
            sendPlayerNames(clientsOculus);
            //startMessageSent = true;

        }, 20000);
    }

    else if (messageString.endsWith(':ready')) {
        // Check if the client's address is already in the list
        const playerName = messageString.split(":")[1]

        if (messageString.startsWith('O')){
            // Check if the client's player name already exists in the list
            const indexOculus = clientsOculus.findIndex(client => client.playerName === playerName);

            if (indexOculus !== -1) {
                // If the player name already exists, update the client's sender info
                clientsOculus[indexOculus].address = senderInfo.address;
                clientsOculus[indexOculus].port = senderInfo.port;
                console.log(`Updated Oculus Client at ${senderInfo.address}:${senderInfo.port}.`);
            } else {
                // If the player name does not exist, add information about the client
                clientsOculus.push({
                    playerName: playerName,
                    address: senderInfo.address,
                    port: senderInfo.port
                });
                console.log(`Added new Oculus Client at ${senderInfo.address}:${senderInfo.port}.`);
                console.log("Updated clients array:", clientsOculus);
            }

            // const clientOculusExists = clientsOculus.some(client => 
            //     client.address === senderInfo.address && client.port === senderInfo.port
            // );
    
            // if (!clientOculusExists) {
            //     // If the client is not in the list, add information about the client
            //     clientsOculus.push({
            //         playerName: playerName,
            //         address: senderInfo.address,
            //         port: senderInfo.port
            //     });
    
            //     //console.log("Updated clients array:", clientsOculus);
            //     console.log(`Oculus Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
                
            //     // Send an acknowledgment back to the client
            //     // server.send('ack', senderInfo.port, senderInfo.address, () => {
            //     //     console.log(`Acknowledgment sent to oculus ${senderInfo.address}:${senderInfo.port}`);
            //     // });
                
            // } else {
            //     console.log(`Oculus Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
            //     //server.send('ha ha', senderInfo.port, senderInfo.address)
            // }
        }
        
        if (messageString.startsWith('R')){
            const indexRpi = clientsRasp.findIndex(client => client.playerName === playerName);

            if (indexRpi !== -1) {
                // If the player name already exists, update the client's sender info
                clientsRasp[indexRpi].address = senderInfo.address;
                clientsRasp[indexRpi].port = senderInfo.port;
                console.log(`Updated Rpi Client at ${senderInfo.address}:${senderInfo.port}.`);
            } else {
                // If the player name does not exist, add information about the client
                clientsRasp.push({
                    playerName: playerName,
                    address: senderInfo.address,
                    port: senderInfo.port
                });
                console.log(`Added new Rpi Client at ${senderInfo.address}:${senderInfo.port}.`);
                console.log("Updated clients array:", clientsRasp);
            }

            // const clientRaspExists = clientsRasp.some(client => 
            //     client.address === senderInfo.address && client.port === senderInfo.port
            // );
    
            // if (!clientRaspExists) {
            //     // If the client is not in the list, add information about the client
            //     clientsRasp.push({
            //         playerName: playerName,
            //         address: senderInfo.address,
            //         port: senderInfo.port
            //     });
    
            //     console.log("Updated clients array:", clientsRasp);
            //     console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} is ready.`);
                
            //     // Send an acknowledgment back to the client
            //     // server.send('ack', senderInfo.port, senderInfo.address, () => {
            //     //     console.log(`Acknowledgment sent to rasp ${senderInfo.address}:${senderInfo.port}`);
            //     // });
                
            // } else {
            //     console.log(`Rasp Client at ${senderInfo.address}:${senderInfo.port} is already in the list.`);
            //     //server.send('ha ha', senderInfo.port, senderInfo.address)
            // }
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
                // need to change
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
    // clientsRasp.forEach((client) => {
    //     server.send(message, client.port, client.address, (error) => {
    //         if (error) {
    //             console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
    //         } else {
    //             console.log(`Message broadcasted to ${client.address}:${client.port}`);
    //         }
    //     });
    // });
}
function broadcastRpi(message){
    
    clientsRasp.forEach((client) => {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                console.error(`Error broadcasting to ${client.address}:${client.port}: ${error.message}`);
            } else {
                console.log(`game create broadcasted to ${client.address}:${client.port}`);
            }
        });
    });
    console.log("game created send")
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

// Function to send player names to clients
function sendPlayerNames(clientList) {
    const playerNames = clientList.map(client => client.playerName).join(':');
    const prefixedMessage = `playerNames:${playerNames}`;
    const message = Buffer.from(prefixedMessage);
    clientList.forEach(client => {
        server.send(message, client.port, client.address, (error) => {
            if (error) {
                console.error(`Error sending message to ${client.playerName}: ${error.message}`);
            } else {
                console.log(`Player names sent to ${client.playerName}`);
            }
        });
    });
}


server.bind(5500);
