import asyncio
import socket

async def udp_send(client_socket, message,i):
    
    send_bytes = f"ndl:{i}:{message}:o".encode('ascii')
    client_socket.send(send_bytes)

async def udp_client_ready(client_socket):
    send_bytes = "ndl:0:ready".encode('ascii')
    client_socket.send(send_bytes)

async def udp_receive(client_socket):
    receive_bytes, _ = client_socket.recvfrom(1024)
    received_string = receive_bytes.decode('ascii')
    print("Message received from the server\n" + received_string)
    return received_string

async def udp_disconnect(client_socket):
    send_bytes = "disconnect".encode('ascii')
    client_socket.send(send_bytes)

async def get_user_input():
    loop = asyncio.get_event_loop()
    user_input = await loop.run_in_executor(None, input, "Enter 'disconnect' to disconnect: ")
    return user_input.strip()

async def udp_test():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_ip = "35.154.53.245"
    server_port = 5500
    client.bind(('0.0.0.0', 5400))
    check = True

    try:
        client.connect((server_ip, server_port))
        await udp_client_ready(client)

        number_of_messages = 1000
        sent_sequence_numbers = set(range(1, number_of_messages + 1))
        received_sequence_numbers = set()

        for i in range(1, number_of_messages + 1):
            message = f"message{i}"
            await udp_send(client,message,i)
       
            received_string = await udp_receive(client)
            received_sequence_numbers.add(int(received_string.split(":")[1]))

        lost_packets = sent_sequence_numbers - received_sequence_numbers
        if lost_packets:
            print(f"Lost packets: {lost_packets}")
            for lost_packet in lost_packets:
                print(f"Message {lost_packet} has been lost.")
        else:
            print("No packets lost.")

        while check:
            received_string = await udp_receive(client)
        

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
    asyncio.run(udp_test())