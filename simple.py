import asyncio
import socket


async def udp_send(client_socket,i):
    send_bytes = f"ndl:{i}:msg:o".encode('ascii')
    client_socket.send(send_bytes)


async def udp_receive(client_socket):
    global rec_own
    global rec_another     
    receive_bytes, _ = client_socket.recvfrom(1024)
    received_string = receive_bytes.decode('ascii')
    print("Message received from the server\n" + received_string)
    if ((received_string != "ready") and (received_string != "ack")):
        parts = received_string.split(":")
    
        rec_client_id, rec_seq_num, rec_message, rec_message_type = parts[0], int(parts[1]), parts[2], parts[3]
        print(rec_client_id)
        if rec_client_id == client_id:
            rec_own += 1
        else:
            rec_another += 1
    return rec_own, rec_another
    

async def udp_client_ready(client_socket):
    send_bytes = "ready".encode('ascii')
    client_socket.send(send_bytes)

async def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "35.154.53.245"
    server_port = 5500
    client.bind(('0.0.0.0', 5400))
    global client_id
    global rec_another 
    global rec_own
    check = True
    rec_own = 0
    rec_another = 0
    number_of_messages = 200
    global sent_sequence_numbers
    global received_sequence_numbers
    sent_sequence_numbers = set(range(1, number_of_messages + 1))
    received_sequence_numbers = set()

    try:
        client.connect((server_ip, server_port))
        print("connected to the server")
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Disconnecting...")
    except Exception as e:
        print("Exception thrown: ", str(e))

    client_id = "ndl"

    await udp_client_ready(client)
    

    for i in range(number_of_messages):# Use asyncio.gather to run multiple coroutines concurrently
        await asyncio.gather(udp_send(client,i),udp_receive(client))
        await asyncio.sleep(0.1)
        print(rec_own, rec_another)
    while check:
        await udp_receive(client)
        print(rec_own, rec_another)
        if rec_own == number_of_messages:
            check = False
        


if __name__ == "__main__":
    asyncio.run(main())
