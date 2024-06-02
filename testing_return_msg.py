import asyncio
import socket
import time

async def udp_send(client_socket, i, timestamps):
    send_bytes = f"Pasi:{i}:msg:o".encode('ascii')
    client_socket.send(send_bytes)
    timestamps[i] = time.time()
    #print(timestamps)

async def udp_send_back(client_socket, send_message):
    send_bytes = send_message.encode('ascii')
    client_socket.send(send_bytes)

async def udp_receive(client_socket, client_id, received_counts, received_sequence_numbers, timestamps, delays, return_counts, return_timestamps, return_delays):
    global rec_own
    global client
    receive_bytes, _ = client_socket.recvfrom(1024)
    received_string = receive_bytes.decode('ascii')
    
    print("Message received from the server " + received_string)
    if received_string != "ready" and received_string != "ack":
        parts = received_string.split(":")
        rec_client_id, rec_seq_num, rec_message, rec_message_type = parts[0], int(parts[1]), parts[2], parts[3]
        
        if rec_message_type == "r":
            #parts = received_string.split(":")
            #rec_client_id, rec_seq_num, rec_message, rec_message_type = parts[0], int(parts[1]), parts[2], parts[3]
            sub_part = rec_client_id.split(",")
            rec_client_id, from_client_id = sub_part[0], sub_part[1]
            
            if  rec_client_id == client_id:
                #print("msg rec from ", rec_client_id)
                #print("Message received from the server\n" + received_string)
                return_counts[from_client_id] = received_counts.get(from_client_id, set())
                return_counts[from_client_id].add(rec_seq_num)
                #print("return_counts",return_counts)
                #print("return_timestamps",return_timestamps)
                sent_time = timestamps.get(rec_seq_num, 0)
                if sent_time != 0:
                    delay = time.time() - sent_time
                    #print(delay)
                    return_delays.append(delay)

                
        elif rec_client_id == client_id:
            #parts = received_string.split(":")
            #rec_client_id, rec_seq_num, rec_message, rec_message_type = parts[0], int(parts[1]), parts[2], parts[3]
            if rec_message_type == "o":
                received_counts[rec_client_id] = received_counts.get(rec_client_id, set())
                received_counts[rec_client_id].add(rec_seq_num)
                rec_own = rec_seq_num
                #print("received_counts", received_counts)
                sent_time = timestamps.get(rec_seq_num, 0)
                
                if sent_time != 0:
                    delay = time.time() - sent_time
                    #print(f"Delay in receiving own message {rec_seq_num}: {delay} seconds")
                    delays.append(delay)
                    #print(delays)
        else:
            #parts = received_string.split(":")
            #rec_client_id, rec_seq_num, rec_message, rec_message_type = parts[0], int(parts[1]), parts[2], parts[3]
            received_counts[rec_client_id] = received_counts.get(rec_client_id, set())
            received_counts[rec_client_id].add(rec_seq_num)
            #print("received_counts", received_counts)
            if rec_message_type == "o":
                send_message = f"{rec_client_id},{client_id}:{rec_seq_num}:{rec_message}:r"
                #print(send_message)
                await udp_send_back(client, send_message)

async def udp_client_ready(client_socket):
    send_bytes = "ready".encode('ascii')
    client_socket.send(send_bytes)

async def main():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "15.206.74.115"
    server_port = 5500
    client.bind(('0.0.0.0', 5400))
    client_id = "Pasi"
    number_of_messages = 5000
    received_counts = {}  # Dictionary to store received message counts for each client
    return_counts = {}   # Dictionary to store returning message counts for each client
    received_sequence_numbers = set(range(1, number_of_messages + 1))
    global rec_own
    rec_own = 0
    timestamps = {}
    return_timestamps = {}
    delays = []
    return_delays = []
    check = True
    check_in = True
    lost = []
    

    try:
        client.connect((server_ip, server_port))
        print("connected to the server")
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Disconnecting...")
    except Exception as e:
        print("Exception thrown: ", str(e))

    await udp_client_ready(client)
    await asyncio.sleep(0.1)

    
    for i in range(1,number_of_messages+1):
        await asyncio.gather(udp_send(client, i, timestamps), udp_receive(client, client_id, received_counts, received_sequence_numbers, timestamps, delays, return_counts, return_timestamps, return_delays))
        while check_in:
            print("in", rec_own, i)
            
            if rec_own < i:
                #print("in")
                time_in = time.time() 
                #print(time_in, timestamps[i])
                if (time_in-timestamps[i]) > 5:
                    print((time_in-timestamps[i]))
                    print(i ,"packet loss")
                    lost.append(i)
                    rec_own += 1
                    check_in = False
                await udp_receive(client, client_id, received_counts, received_sequence_numbers, timestamps, delays, return_counts, return_timestamps, return_delays)

            else:
                check_in = False
        check_in = True
        await asyncio.sleep(0.1)
    
    # Check for lost packets for each client
    while check:
        if rec_own == number_of_messages:
            check = False
            for client_id, count in received_counts.items():
                #print(received_counts)
                expected_sequence_numbers = set(range(1, number_of_messages + 1))
                lost_packets = expected_sequence_numbers - received_sequence_numbers
                if lost_packets:
                    print(f"Client {client_id} lost packets: {lost_packets}")
                    for lost_packet in lost_packets:
                        print(f"Message {lost_packet} from client {client_id} has been lost.")
                else:
                    print(f"Client {client_id}: No packets lost.")
            break
        else:
            await udp_receive(client, client_id, received_counts, received_sequence_numbers, timestamps, delays, return_counts, return_timestamps, return_delays)
    '''print("return_counts", return_counts)
    print("delays",delays)
    print("len delays", len(delays))
    print("return delays",return_delays)
    print("len return delays", len(return_delays))'''
    if delays:
        average_delay = (sum(delays) / len(delays)) * 1000
        print(f"Average delay in receiving own messages: {average_delay} milliseconds")
    
    if return_delays:
        average_return_delay = (sum(return_delays) / (2*len(return_delays))) * 1000
        print(f"Average return delay in receiving own messages: {average_return_delay} milliseconds")
    '''if return_counts:
        return_packets = sum(return_counts.values())
        print(f"Packet loss in returning messages: {number_of_messages - return_packets}/{number_of_messages}")'''
    print(received_counts[client_id])
    print(lost)
if __name__ == "__main__":
    asyncio.run(main())
