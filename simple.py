import asyncio
import socket

async def udp_send(client_socket,i):
    
        print("in send fn")
        send_bytes = f"ndl:{i}:msg:o".encode('ascii')
        client_socket.send(send_bytes)


async def udp_receive(client_socket):
    
        print("in rec fn")
        receive_bytes, _ = client_socket.recvfrom(1024)
        received_string = receive_bytes.decode('ascii')
        print("Message received from the server\n" + received_string)

async def udp_client_ready(client_socket):
    send_bytes = "ready".encode('ascii')
    client_socket.send(send_bytes)

async def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "35.154.53.245"
    server_port = 5500
    client.bind(('0.0.0.0', 5400))
    


    try:
        client.connect((server_ip, server_port))
        print("connected to the server")
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Disconnecting...")
    except Exception as e:
        print("Exception thrown: ", str(e))

    await udp_client_ready(client)
    for i in range(10):# Use asyncio.gather to run multiple coroutines concurrently
        await asyncio.gather(udp_send(client,i),udp_receive(client))
        


if __name__ == "__main__":
    asyncio.run(main())
