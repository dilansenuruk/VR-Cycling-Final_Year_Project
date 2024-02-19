import asyncio
import socket
import time

async def udp_send(client_socket, i, timestamps):
    send_bytes = f"ndl:{i}:msg:o".encode('ascii')
    client_socket.send(send_bytes)
    timestamps[i] = time.time()
    #print(timestamps)

async def udp_receive(client_socket, client_id, received_counts, received_sequence_numbers, timestamps, delays):
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
            
            sent_time = timestamps.get(rec_seq_num, 0)
            if sent_time != 0:
                delay = time.time() - sent_time
                print(f"Delay in receiving own message {rec_seq_num}: {delay} seconds")
                delays.append(delay)
        else:
            received_counts[rec_client_id] = received_counts.get(rec_client_id, 0) + 1

async def udp_client_ready(client_socket):
    send_bytes = "ready".encode('ascii')
    client_socket.send(send_bytes)

async def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "13.233.195.226"
    server_port = 5500
    client.bind(('0.0.0.0', 5400))
    client_id = "ndl"
    number_of_messages = 10
    received_counts = {}  # Dictionary to store received message counts for each client
    received_sequence_numbers = set(range(1, number_of_messages + 1))
    global rec_own
    rec_own = 0
    timestamps = {}
    delays = []
    check = True
    

    try:
        client.connect((server_ip, server_port))
        print("connected to the server")
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Disconnecting...")
    except Exception as e:
        print("Exception thrown: ", str(e))

    await udp_client_ready(client)
    
    for i in range(1,number_of_messages+1):
        await asyncio.gather(udp_send(client, i, timestamps), udp_receive(client, client_id, received_counts, received_sequence_numbers, timestamps, delays))  
        await asyncio.sleep(0.1)
    
    # Check for lost packets for each client
    while check:
        #print("in while")
          # 5 seconds timeout, adjust as needed
        #print(rec_own)

        if rec_own == number_of_messages:
            check = False
            for client_id, count in received_counts.items():
                print(received_counts)
                expected_sequence_numbers = set(range(1, number_of_messages + 1))
                lost_packets = expected_sequence_numbers - received_sequence_numbers
                if lost_packets:
                    print(f"Client {client_id} lost packets: {lost_packets}")
                    for lost_packet in lost_packets:
                        print(f"Message {lost_packet} from client {client_id} has been lost.")
                else:
                    print(f"Client {client_id}: No packets lost.")
            #break
        else:
            await udp_receive(client, client_id, received_counts, received_sequence_numbers, timestamps, delays)

    
    if delays:
        average_delay = (sum(delays) / len(delays))*1000
        print(f"Average delay in receiving own messages: {average_delay} miliseconds")
    #await udp_receive(client, client_id, received_counts, received_sequence_numbers, timestamps, delays)

if __name__ == "__main__":
    asyncio.run(main())
