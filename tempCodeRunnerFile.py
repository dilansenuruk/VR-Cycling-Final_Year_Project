lost_packets = sent_sequence_numbers - received_sequence_numbers
        if lost_packets:
            print(f"Lost packets: {lost_packets}")
            for lost_packet in lost_packets:
                print(f"Message {lost_packet} has been lost.")
        else:
            print("No packets lost.")