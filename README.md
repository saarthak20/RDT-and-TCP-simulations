

## Overview

This project implements simulations of core **reliable data transfer** and **TCP congestion control** mechanisms as part of Computer Networks coursework:

1. **RDT 2.2** (NAK-free reliable data transfer)
2. **RDT 3.0** (reliable data transfer over a lossy channel)
3. **TCP Tahoe** congestion control
4. **TCP Reno** congestion control

## Features

* **RDT 2.2:**

  * Simulates FSM for sender and receiver.
  * Injects configurable packet corruption (0–10%).
  * Hardcoded packets for controlled simulation.

* **RDT 3.0:**

  * Adds packet loss simulation and timer-based retransmissions.
  * Configurable corruption and loss probabilities (0–10%).
  * Uses hardcoded packets for testing.

* **TCP Tahoe:**

  * Implements slow start and congestion control with CWND adjustments.
  * Configurable MSS, RTTs, initial ssthresh, and loss intervals.
  * Plots CWND and RTT progression using `matplotlib`.

* **TCP Reno:**

  * Similar to Tahoe, with additional fast recovery state.
  * Simulates timeout and duplicate ACK handling.
  * Configurable MSS, RTTs, initial ssthresh, loss intervals, and duplicate ACK intervals.
  * Visualizes CWND and thresholds using `matplotlib`.

## Usage

* Ensure **Python 3.x** is installed.
* Install dependencies (if using plotting):

```bash
pip install matplotlib
```

* Run each Python file corresponding to the protocol you want to simulate.

## Notes

* Hardcoded message packets are used for controlled and illustrative simulations.
* Outputs include printed simulation states and plots for congestion control behavior.

---


