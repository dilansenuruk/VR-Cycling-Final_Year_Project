import asyncio
import socket

async def udp_send(client_socket, i):
    send_bytes = f"ndl:{i}:msg:o".encode('ascii')
    client_socket.send(send_bytes)

async def udp_receive(client_socket, client_id, received_counts, received_sequence_numbers):
    global rec_own
    receive_bytes, _ = client_socket.recvfrom(1024)
    received_string = receive_bytes.decode('ascii')
    
    print("Message received from the server\n" + received_string)
    if received_string != "ready" and received_string != "ack":
        parts = received_string.split(":")
        rec_client_id, rec_seq_num, rec_message, rec_message_type = parts[0], int(parts[1]), parts[2], parts[3]
        
        #print(rec_client_id)
        if rec_client_id == client_id:
            received_counts[rec_client_id] = received_counts.get(rec_client_id, 0) + 1
            rec_own += 1
        else:
            received_counts[rec_client_id] = received_counts.get(rec_client_id, 0) + 1

async def udp_client_ready(client_socket):
    send_bytes = "ready".encode('ascii')
    client_socket.send(send_bytes)

async def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "35.154.53.245"
    server_port = 5500
    client.bind(('0.0.0.0', 5400))
    client_id = "ndl"
    number_of_messages = 100
    received_counts = {}  # Dictionary to store received message counts for each client
    received_sequence_numbers = set(range(1, number_of_messages + 1))
    global rec_own
    rec_own = 0
    

    try:
        client.connect((server_ip, server_port))
        print("connected to the server")
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Disconnecting...")
    except Exception as e:
        print("Exception thrown: ", str(e))

    await udp_client_ready(client)
    
    for i in range(1,number_of_messages+1):
        await asyncio.gather(udp_send(client, i), udp_receive(client, client_id, received_counts, received_sequence_numbers))  
        await asyncio.sleep(0.1)
    
    # Check for lost packets for each client
    while True:
        print("in while")
        #await udp_receive(client, client_id, received_counts, received_sequence_numbers)  # 5 seconds timeout, adjust as needed
        print(rec_own)

        if rec_own == number_of_messages:
            for client_id, count in received_counts.items():
                #print("rec", received_sequence_numbers)
                expected_sequence_numbers = set(range(1, number_of_messages + 1))
                lost_packets = expected_sequence_numbers - received_sequence_numbers
                if lost_packets:
                    print(f"Client {client_id} lost packets: {lost_packets}")
                    for lost_packet in lost_packets:
                        print(f"Message {lost_packet} from client {client_id} has been lost.")
                else:
                    print(f"Client {client_id}: No packets lost.")
            break

if __name__ == "__main__":
    asyncio.run(main())
