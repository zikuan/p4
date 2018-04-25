# Instructions

## Introduction

In this tutorial, you will implement a heavy hitter detection filter.

Network flows typically have a fairly wide distribution in terms of the 
data they transmit, with most of the flows sending little data and few
flows sending a lot. The latter flows are called heavy hitters, and they
often have a detrimental effect to network performance. This is
because they cause congestion, leading to significantly increased completion
times for small, short-lived flows. Detecting heavy hitters allows us to treat them 
differently, e.g. we can put their packets in low priority queues, allowing
packets of other flows to face little or no congestion.

In this example, you will implement a heavy hitter detection filter within 
a router. You can find a skeleton of the program in simple_router.p4. In that
file, you have to fill in the parts that are marked with TODO.

This example is based on [count-min sketch](http://theory.stanford.edu/~tim/s15/l/l2.pdf).
In fact, we use two count-min sketches which are reset with an offset
equal to their half-life. With every new packet coming in, we update
the values of both sketches but we use only the ones of the least 
recently reset one to decide whether a packet belongs to a heavy hitter
flow or not.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.


## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`simple_router.p4`, which implements a simple router. Your job will be to
extend this skeleton program to properly implement a heavy hitter
detection filter.

Before that, let's compile the incomplete `simple_router.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   ./run.sh
   ```
   This will:
   * create a p4app application,
   * compile `simple_switch.p4`,
   * generate control plane code,
   * start a Mininet instance with one switch (`s1`) conected to
	 two hosts (`h1` and `h2`).
   * install the control plane code to your switch,
   * The hosts are assigned IPs of `10.0.0.10` and `10.0.1.10`.

2. You should now see a Mininet command prompt. Run ping between
   `h1` and `h2` to make sure that everything runs correctly:
   ```bash
   mininet> h1 ping h2
   ```
   You should see all packets going through.

3. Type `exit` to leave each Mininet command line.

### A note about the control plane

A P4 program defines a packet-processing pipeline, but the rules
within each table are inserted by the control plane. When a rule
matches a packet, its action is invoked with parameters supplied by
the control plane as part of the rule.

In this exercise, we have already implemented the control plane
logic for you. As part of invoking `run.sh`, a set of rules is generated
by `setup.py` and when bringing up the Mininet instance, these
packet-processing rules are installed in the tables of
the switch. These are defined in the `simple_router.config` file.

## Step 2: Implement the heavy hitter detection filter

The `simple_router.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments. Your implementation should follow
the structure given in this file, just replace each `TODO` with logic
implementing the missing piece.

More specifically, you need to implement the main actions used within
the heavy hitter detection block. In this example, when our filter
classifies a packet as belonging to a heavy hitter flow, it marks
it as such and then the switch drops it before reaching the 
egress control.

## Step 3: Run your solution

Our heavy hitter filter requires periodic reset of the registers of the
count-min sketches. Running:
```bash
bash filter_reset.sh
```
in a terminal window does that periodic reset for you.

The filter currently allows 1000 bytes/sec (you can change that value
in `setup.py`).

In another terminal window, run:
```bash
./run.sh
```

In the minigraph window, you can try:
```
h1 ping -s 80 -i 0.1 h2
```
With this command h1, sends a packet with a total IP length
of 100 bytes every 100 ms. When you run this command, you
shouldn't see any drops. If on the other hand you run:
```
h1 ping -s 80 -i 0.05 h2
```
h1 sends a packet every 50 ms, which puts the flow above
the filter limit. In this case you will observe that about
half of the packets send by h1 are being dropped at the switch.

### Next steps
Check out the code in `setup.py` and `filter_reset.sh`. By changing
the constants in those, you can experiment with different 
heavy hitter threshold levels, count-min sketch sizes and the accuracy
of the throughput approximation.

