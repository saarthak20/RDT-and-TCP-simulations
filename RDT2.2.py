import random

msg = ["msg1", "msg2", "msg3", "msg4", "msg5"]
result = [] 
last_delivered_seq_num = -1

prob =float(input("Enter how much error probabilty do you want? (between 0 to 0.1): "))
if prob>0.1 or prob < 0:
    prob  = float(input("Enter a valid number(0 to 0.1): "))

class Packet:
    def __init__(self, seq_num, data):
        self.seq_num = seq_num  # 0 or 1
        self.data = data
        self.checksum = self.compute_checksum()

    def compute_checksum(self):
        return sum(bytearray(self.data.encode())) + self.seq_num
    
    def corrupt(self):
        return self.compute_checksum() != self.checksum

def error_simulation(pack):
    if random.random() < prob:  
        byte_array = bytearray(pack.data.encode())
        no_flips = random.randint(1, len(byte_array))
        for _ in range(no_flips):
            byte_index = random.randint(0, len(byte_array) - 1)
            bit_index = random.randint(0, 7)
            byte_array[byte_index] ^= 1 << bit_index
        pack.data = byte_array.decode(errors='ignore')
        return pack
    return pack

def simulate_ack_error(ack):
    if random.random() < prob:  
        byte_array = bytearray(ack.data.encode())
        byte_index = random.randint(0, len(byte_array) - 1)
        bit_index = random.randint(0, 7)
        byte_array[byte_index] ^= 1 << bit_index
        ack.data = byte_array.decode(errors='ignore')
    return ack

def sender_fsm_state0():
    if not msg:
        print("All data sent. Transmission complete.")
        return

    byte_data = msg.pop()
    sqno = 0
    pack = Packet(sqno, byte_data)
    print(100*"-")
    print("Sender : Got call 0 from above , Packet made")
    print(f"Sender : Seq={pack.seq_num}, Checksum={pack.checksum}, Data={pack.data}")
    sender_fsm_state1(pack)

def sender_fsm_state1(pack):
    print("Sender : Sent Packet")
    ack_rec = reciver_fsm_state0(pack)
    retries = 0
    while (ack_rec.seq_num != pack.seq_num or ack_rec.corrupt()):
        print(f"Sender : Wrong/corrupted ACK (Seq={ack_rec.seq_num}, Checksum={ack_rec.checksum}) -> Resending")
        ack_rec = reciver_fsm_state0(pack)
        retries += 1
        if retries > 10:
            print("Sender: Too many retries, aborting.")
            return
    print("Sender : Recived correct ACK")
    print(100*"-")
    sender_fsm_state2()

def sender_fsm_state2():
    if not msg:
        print("All data sent. Transmission complete.")
        return

    print(100*"-")
    print("Sender : Got call 1 from above , Packet made")
    byte_data = msg.pop()
    sqno = 1
    pack = Packet(sqno, byte_data)
    print(f"Sender : Seq={pack.seq_num}, Checksum={pack.checksum}, Data={pack.data}")
    sender_fsm_state3(pack)

def sender_fsm_state3(pack):
    print("Sender : Sent Packet")
    ack_rec = reciver_fsm_state1(pack)
    retries = 0
    while (ack_rec.seq_num != pack.seq_num or ack_rec.corrupt()):
        print(f"Sender : Wrong/corrupted ACK (Seq={ack_rec.seq_num}, Checksum={ack_rec.checksum}) -> Resending")
        ack_rec = reciver_fsm_state1(pack)
        retries += 1
        if retries > 10:
            print("Sender: Too many retries, aborting.")
            return
    print("Sender : Recived correct ACK")
    print(100*"-")
    sender_fsm_state0()

def reciver_fsm_state0(pack):
    global last_delivered_seq_num
    print("Reciver : Recived Packet")
    pack = error_simulation(pack)

    if not pack.corrupt() and pack.seq_num == 0:
        if last_delivered_seq_num != 0:
            print("Reciver : No error found , delivering data and sending ACK")
            result.append(pack.data)
            last_delivered_seq_num = 0
        else:
            print("Reciver : Duplicate packet detected, resending ACK")
        ack = Packet(0, "ACK")
        return simulate_ack_error(ack)
    else:
        print("Reciver : Error found")
        ack = Packet(1, "ACK")
        return simulate_ack_error(ack)


def reciver_fsm_state1(pack):
    global last_delivered_seq_num
    print("Reciver : Recived Packet")
    pack = error_simulation(pack)

    if not pack.corrupt() and pack.seq_num == 1:
        if last_delivered_seq_num != 1:
            print("Reciver : No error found , delivering data and sending ACK")
            result.append(pack.data)
            last_delivered_seq_num = 1
        else:
            print("Reciver : Duplicate packet detected, resending ACK")
        ack = Packet(1, "ACK")
        return simulate_ack_error(ack)
    else:
        print("Reciver : Error found")
        ack = Packet(0, "ACK")
        return simulate_ack_error(ack)


# START THE SENDER FSM
sender_fsm_state0()

print("\nFinal received messages at receiver:")
print(result)
