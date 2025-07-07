x = []
y = []
threshold_y = []

mss = int(input("Enter MSS: "))
ssthresh = int(input("Enter initial ssthresh: "))
RTT = int(input("Enter total RTTs: "))
loss_input = input("Enter loss event RTTs (space-separated): ").split()
loss = set(map(int, loss_input))  # convert to set of ints for fast lookup

cwnd = 1 * mss
y.append(cwnd)
x.append(1)
threshold_y.append(ssthresh)
i = 2  # RTT index


def slow_start():
    global i, cwnd, ssthresh
    while i < RTT:
        if i in loss:
            print(f"[RTT {i}] LOSS occurred! Resetting to slow start.")
            ssthresh = cwnd // 2
            cwnd = mss
            y.append(cwnd)
            x.append(i)
            threshold_y.append(ssthresh)
            i += 1

        else:
            if cwnd < ssthresh:
                if cwnd*2 < ssthresh:
                    cwnd *= 2
                    y.append(cwnd)
                    x.append(i)
                    threshold_y.append(ssthresh)

                    print(f"[RTT {i}] Slow Start: cwnd = {cwnd}")
                else:
                    cwnd = ssthresh
                    y.append(cwnd)
                    x.append(i)
                    threshold_y.append(ssthresh)

                    print(f"[RTT {i}] Slow Start: cwnd = {cwnd}")


            else:
                print(f"[RTT {i}] Switching to congestion avoidance.")
                congestion_avoidance()
                return
            i += 1

def congestion_avoidance():
    global i, cwnd, ssthresh
    while i < RTT:
        
        if i in loss:
            #print(f"[RTT {i}] LOSS occurred! Resetting to slow start.")
            ssthresh = cwnd // 2
            cwnd = mss
            y.append(cwnd)
            x.append(i)
            threshold_y.append(ssthresh)
            i += 1
            slow_start()
            return
        else:
            cwnd += 1
            y.append(cwnd)
            x.append(i)
            threshold_y.append(ssthresh)

            print(f"[RTT {i}] Congestion Avoidance: cwnd = {cwnd}")
            i += 1

# Run the simulation
slow_start()

print(x)
print(y)
print(threshold_y)

# Plot the result
import matplotlib.pyplot as plt

plt.plot(x, y, marker='o')
plt.plot(x, threshold_y, linestyle='--', color='red', label='ssthresh (Threshold)')
plt.xlabel("Number of RTT")
plt.ylabel("Congestion Window (cwnd)")
plt.title("TCP Tahoe Congestion Control")
plt.text(x[-1], threshold_y[-1], 'Threshold', fontsize=10, color='green', verticalalignment='bottom')
plt.grid(True)
plt.show()
