import matplotlib.pyplot as plt

x = []
y = []
threshold_y = []


mss = int(input("Enter MSS: "))
ssthresh = int(input("Enter initial ssthresh: "))
RTT = int(input("Enter total RTTs: "))
dup_ack_rtt = int(input("Enter RTT for triple duplicate ACK (e.g., 9): "))
timeout_input = input("Enter RTTs for TIMEOUTs (space-separated, optional): ").split()
timeout_rtts = set(map(int, timeout_input)) if timeout_input != [''] else set()

cwnd = 1 * mss
i = 1
state = "SLOW_START"
in_fast_recovery = False
dup_ack_handled = False  # To trigger triple dup ACK only once


x.append(i)
y.append(cwnd)
threshold_y.append(ssthresh)

def log_point():
    x.append(i)
    y.append(cwnd)
    threshold_y.append(ssthresh)

i += 1  

while i <= RTT:
    if i in timeout_rtts:
        print(f"[RTT {i}] TIMEOUT occurred! Falling back to slow start.")
        ssthresh = cwnd // 2
        cwnd = 1 * mss
        state = "SLOW_START"
        log_point()
        i += 1
        continue

    if i == dup_ack_rtt and not dup_ack_handled:
        print(f"[RTT {i}] Triple Duplicate ACK detected — Fast Recovery begins.")
        ssthresh = cwnd // 2
        cwnd = ssthresh + 3 * mss  
        in_fast_recovery = True
        state = "FAST_RECOVERY"
        dup_ack_handled = True
        log_point()
        i += 1
        continue

    if state == "SLOW_START":
        if cwnd < ssthresh:
            cwnd *= 2
            print(f"[RTT {i}] Slow Start: cwnd = {cwnd}")
        else:
            print(f"[RTT {i}] Reached ssthresh, switching to Congestion Avoidance.")
            cwnd += 1 * mss
            state = "CONGESTION_AVOIDANCE"
        log_point()

    elif state == "CONGESTION_AVOIDANCE":
        cwnd += 1 * mss
        print(f"[RTT {i}] Congestion Avoidance: cwnd = {cwnd}")
        log_point()

    elif state == "FAST_RECOVERY":
        print(f"[RTT {i}] ACK for lost packet received. Exiting Fast Recovery.")

        cwnd += 1 * mss
        state = "CONGESTION_AVOIDANCE"
        in_fast_recovery = False
        log_point()

    i += 1

# Plotting
plt.plot(x, y, marker='o', label='cwnd (Congestion Window)', color='black')
plt.plot(x, threshold_y, linestyle='--', color='gray', label='ssthresh (Threshold)')
plt.text(x[-1], threshold_y[-1], 'Threshold', fontsize=10, color='green', verticalalignment='bottom')
plt.xlabel("RTT")
plt.ylabel("Congestion Window (in segments)")
plt.title("TCP Reno Congestion Control")
plt.legend()
plt.grid(True)
plt.show()
