import random
import time
import threading

msg = ["msg1", "msg2", "msg3", "msg4", "msg5"]
result = [] 
last_delivered_seq_num = -1

prob1 =float(input("Enter how much error probabilty do you want? (between 0 to 0.1): "))
if prob1>0.1 or prob1 < 0:
    prob1 = float(input("Enter a valid number(0 to 0.1): "))

prob2 =float(input("Enter how much packet loss probabilty do you want? (between 0 to 0.1): "))
if prob2>0.1 or prob2 < 0:
    prob2 = float(input("Enter a valid number(0 to 0.1): "))

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
    if random.random() < prob1:  
        byte_array = bytearray(pack.data.encode())
        no_flips = random.randint(1, len(byte_array))
        for _ in range(no_flips):
            byte_index = random.randint(0, len(byte_array) - 1)
            bit_index = random.randint(0, 7)
            byte_array[byte_index] ^= 1 << bit_index
        pack.data = byte_array.decode(errors='ignore')
        return pack
    return pack

def simulate_packet_loss():

    return random.random() < prob2

def simulate_ack_error(ack):
    if random.random() < prob1: 
        byte_array = bytearray(ack.data.encode())
        byte_index = random.randint(0, len(byte_array) - 1)
        bit_index = random.randint(0, 7)
        byte_array[byte_index] ^= 1 << bit_index
        ack.data = byte_array.decode(errors='ignore')
    return ack

def simulate_ack_loss():

    return random.random() < prob2

# Timer related functions
class PacketTimer:
    def __init__(self, timeout=1.0):
        self.timeout = timeout
        self.timer = None
        self.expired = False
    
    def start(self):
        self.expired = False
        self.timer = threading.Timer(self.timeout, self.timeout_handler)
        self.timer.start()
    
    def stop(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None
    
    def timeout_handler(self):
        print("Timer: Timeout occurred!")
        self.expired = True

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
    timer = PacketTimer(timeout=1.0)  
    retries = 0
    max_retries = 10
    
    def send_packet():
        print("Sender : Sent Packet")
        # Simulate packet loss
        if not simulate_packet_loss():
            return reciver_fsm_state0(pack)
        else:
            print("Sender : Packet lost in transmission")
            return None

    timer.start()
    ack_rec = send_packet()
    
    while True:
        
        if retries >= max_retries:
            print("Sender: Too many retries, aborting.")
            timer.stop()
            return
            
        
        if timer.expired:
            print("Sender : Timeout -> Resending packet")
            timer.stop()
            timer = PacketTimer(timeout=1.0)
            timer.start()
            retries += 1
            print(f"Sender : Retry attempt {retries}/{max_retries}")
            ack_rec = send_packet()
            continue
            
        
        if ack_rec is None:
            time.sleep(0.1)  
            continue
            
        
        if ack_rec.seq_num != pack.seq_num or ack_rec.corrupt():
            print(f"Sender : Wrong/corrupted ACK (Seq={ack_rec.seq_num}, Checksum={ack_rec.checksum}) -> Ignoring")
            time.sleep(0.1)  
            continue
            
        timer.stop()
        print("Sender : Received correct ACK")
        print(100*"-")
        sender_fsm_state2()
        return

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
    timer = PacketTimer(timeout=1.0) 
    retries = 0
    max_retries = 10
    
    def send_packet():
        print("Sender : Sent Packet")

        if not simulate_packet_loss():
            return reciver_fsm_state1(pack)
        else:
            print("Sender : Packet lost in transmission")
            return None

    timer.start()
    ack_rec = send_packet()
    
    while True:

        if retries >= max_retries:
            print("Sender: Too many retries, aborting.")
            timer.stop()
            return
            

        if timer.expired:
            print("Sender : Timeout -> Resending packet")
            timer.stop()
            timer = PacketTimer(timeout=1.0)
            timer.start()
            retries += 1
            print(f"Sender : Retry attempt {retries}/{max_retries}")
            ack_rec = send_packet()
            continue
            

        if ack_rec is None:
            time.sleep(0.1)  
            continue
            

        if ack_rec.seq_num != pack.seq_num or ack_rec.corrupt():
            print(f"Sender : Wrong/corrupted ACK (Seq={ack_rec.seq_num}, Checksum={ack_rec.checksum}) -> Ignoring")
            time.sleep(0.1)  
            continue
            

        timer.stop()
        print("Sender : Received correct ACK")
        print(100*"-")
        sender_fsm_state0()
        return

def reciver_fsm_state0(pack):
    global last_delivered_seq_num
    print("Receiver : Received Packet")
    pack = error_simulation(pack)

    if not pack.corrupt() and pack.seq_num == 0:
        if last_delivered_seq_num != 0:
            print("Receiver : No error found, delivering data and sending ACK")
            result.append(pack.data)
            last_delivered_seq_num = 0
        else:
            print("Receiver : Duplicate packet detected, resending ACK")
        ack = Packet(0, "ACK")

        if simulate_ack_loss():
            print("Receiver : ACK lost in transmission")
            return None
        return simulate_ack_error(ack)
    else:
        print("Receiver : Error found")
        ack = Packet(1, "ACK")

        if simulate_ack_loss():
            print("Receiver : ACK lost in transmission")
            return None
        return simulate_ack_error(ack)


def reciver_fsm_state1(pack):
    global last_delivered_seq_num
    print("Receiver : Received Packet")
    pack = error_simulation(pack)

    if not pack.corrupt() and pack.seq_num == 1:
        if last_delivered_seq_num != 1:
            print("Receiver : No error found, delivering data and sending ACK")
            result.append(pack.data)
            last_delivered_seq_num = 1
        else:
            print("Receiver : Duplicate packet detected, resending ACK")
        ack = Packet(1, "ACK")

        if simulate_ack_loss():
            print("Receiver : ACK lost in transmission")
            return None
        return simulate_ack_error(ack)
    else:
        print("Receiver : Error found")
        ack = Packet(0, "ACK")

        if simulate_ack_loss():
            print("Receiver : ACK lost in transmission")
            return None
        return simulate_ack_error(ack)



print("Starting RDT 3.0 protocol simulation...")
print(f"Channel conditions: {prob1*100}% corruption chance, {prob2*100}% packet loss chance")
sender_fsm_state0()

print("\nFinal received messages at receiver:")
print(result)