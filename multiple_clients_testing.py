import asyncio
import socket

async def udp_send(client_socket, message, seq_num, client_id, message_type):
    send_bytes = f"{client_id}:{seq_num}:{message}:{message_type}".encode('ascii')
    client_socket.send(send_bytes)

async def udp_client_ready(client_socket):
    send_bytes = "0:0:ready:original".encode('ascii')
    client_socket.send(send_bytes)

async def udp_receive(client_socket, client_sequence_numbers):
    while True:
        receive_bytes, _ = client_socket.recvfrom(1024)
        received_string = receive_bytes.decode('ascii')
        print("Message received from the server\n" + received_string)

        parts = received_string.split(":")
        client_id, seq_num, message, message_type = parts[0], int(parts[1]), parts[2], parts[3]

        if message_type == "return":
            print(f"Received return message from {client_id}, seq_num: {seq_num}")
        else:
            client_sequence_numbers[client_id].add(seq_num)
            return_message = f"{client_id}:{seq_num}:{message}:return"
            await udp_send(client_socket, return_message, seq_num, client_id, "return")

async def udp_disconnect(client_socket):
    send_bytes = "0:0:disconnect:original".encode('ascii')
    client_socket.send(send_bytes)

async def get_user_input():
    loop = asyncio.get_event_loop()
    user_input = await loop.run_in_executor(None, input, "Enter 'disconnect' to disconnect: ")
    return user_input.strip()

async def udp_test(client_id, server_address):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.bind(('0.0.0.0', 0))

    try:
        # Connect to the server
        server_ip, server_port = server_address
        client.connect((server_ip, server_port))
        await udp_client_ready(client)

        number_of_messages = 1000
        sent_sequence_numbers = set(range(1, number_of_messages + 1))
        received_sequence_numbers = set()
        client_sequence_numbers = {client_id: set()}

        for i in range(1, number_of_messages + 1):
            message = f"message{i}"
            await udp_send(client, message, i, client_id, "original")

        # Receive messages from the server until a specific condition is met
        await asyncio.gather(udp_receive(client, client_sequence_numbers))

        lost_packets = sent_sequence_numbers - received_sequence_numbers
        if lost_packets:
            print(f"Lost packets: {lost_packets}")
            for lost_packet in lost_packets:
                print(f"Message {lost_packet} has been lost.")
        else:
            print("No packets lost.")

        await asyncio.sleep(1)  # Allow some time for return messages to arrive

        print("Round trip delay measurements:")
        for seq_num in client_sequence_numbers[client_id]:
            print(f"Message {seq_num} - Round trip delay: {seq_num * 0.001} seconds")

        await udp_disconnect(client)

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Disconnecting...")
        await udp_disconnect(client)
    except Exception as e:
        print("Exception thrown: ", str(e))
    finally:
        try:
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except Exception as e:
            print("Exception thrown during socket closure: ", str(e))

if __name__ == "__main__":
    server_address = ("35.154.53.245", 5500)  # Replace with the actual server address
    client_id = input("Enter client ID: ")  # Assuming each client has a unique ID
    asyncio.run(udp_test(client_id, server_address))
