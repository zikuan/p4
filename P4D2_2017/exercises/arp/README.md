# Implementing an ARP/ICMP Responder

## Introduction

This exercise extends the [IPv4 Forwarding](../ipv4_forward) program to
allow your switches to respond to ARP and ICMP requests.  Once implemented,
your hosts will be able to `ping` other hosts connected to the switch, and
have the switch respond. 

This exercise makes several simplifying assumptions:

1. The network topology contains exactly one switch and two hosts.
1. ARP and ICMP requests to the hosts are ignored; only requests sent to the
   switch receive responses.

Implementing the full functionality of ARP and ICMP is straightforward but
beyond the scope of this tutorial and left as an exercise to the reader.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the reference.

## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`arp.p4`, which initially drops all packets.  Your job will be to
extend it to reply to ARP and ICMP requests.

As a first step, compile the incomplete `arp.p4` and bring up a
switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   ./run.sh
   ```
   This will:
   * compile `arp.p4`, and
   * start a Mininet instance with one switch (`s1`) connected to two hosts (`h1`, `h2`).
   * The hosts are assigned IPs of `10.0.1.10` and `10.0.2.10`.

2. Once the P4 source compiles without error, you can test your program at the
mininet prompt using the `ping` utility.

    ``` mininet> h1 ping h2 ```

    Once the program is implemented correctly, you will see a response to the
    ping in the mininet window.

3. Type `exit` in the mininet terminal to exit.


### A note about the control plane

P4 programs define a packet-processing pipeline, but the rules governing packet
processing are inserted into the pipeline by the control plane.  When a rule
matches a packet, its action is invoked with parameters supplied by the control
plane as part of the rule.

In this exercise, the control plane logic has already been implemented.  As
part of bringing up the Mininet instance, the `run.sh` script will install
packet-processing rules in the tables of each switch.  These are defined in the
`simple_router.config` file.


## Step 2: Implement ARP/ICMP Replies

In this exercise, we are using entries in the `ipv4_lpm` table as a
database, which we can reference when responding to ARP and ICMP requests.
Without the proper entries in the table, the solution will not work.

From a high-level, the task involves implementing two main components: ARP
replies and ICMP replies.

### ARP Reply

When the switch receives and ARP request asking to resolve the switch's IP
address, it will need to perform the following actions:

1. Swap the source and destination MAC addresses in the Ethernet header,
1. set the ARP operation to ARP_REPLY (`2`) in the ARP header,
1. update the sender hardware address (SHA) and sender protocol address (SPA) in the ARP header to
be the MAC and IP addresses of the switch, and
1. set the target hardware address (THA) and target protocol address (TPA) to be the SHA
and SPA of the arriving ARP packet.

### ICMP Reply

When the switch receives and ICMP request containing the switch's IP and MAC
addresses, it will need to perform the following actions: 

1.  Swap the source and destination MAC addresses in the Ethernet header, 
1.  swap the source and destination IP addresses in the ICMP header, and 
1.  set the type field in the ICMP header to `ICMP_ECHO_REPLY` (`0`).
1.  To simplify the exercise, we can ignore the checksum by setting to checksum
    field to 0.


We have provided a skeleton `arp.p4` file to get you started. In this
file, places to modify are marked by `TODO`.

There are, of course, different possible solutions. We describe one approach
below. It builds on the [IPv4 Forwarding](../ipv4_forward) solution, which
used the table `ipv4_lpm` for L3 forwarding, by adding a second table named
`forward`, which checks if a packet is an ARP or ICMP packet and invokes
actions to send an ARP reply, forward an IPv4 packet, or send an ICMP reply.

Broadly speaking, a complete solution will contain the following components:

1. Header type definitions for `ethernet_t`, `arp_t`, `ipv4_t`, and `icmp_t`.

1. A structure (named `my_metadata_t` in `arp.p4`) with metadata fields for the
packet's souce and destination MAC addresses, IPv4 address, egress port, as
well as a hard-coded MAC address for the switch.

1. **TODO:** Parsers for Ethernet, ARP, IPv4, and ICMP packet header types.

1. **TODO:** A control type declaration for ingress processing, containing:

    1. An action for `drop`.

    1. An action (named `ipv4_forward`) to store information in the metadata
    structure, rather than immediately writing to the packet header.

    1. A table (named `ipv4_lpm`) that will match on the destination IP address
    and invoke the `ipv4_forward` action.

    1. An action to send an ICMP reply.

    1. An action to send an ARP reply.

    1. A table (named `forward`) that will forward IPv4 packets, send an ARP
    reply, send an ICMP reply, or drop a packet.

    1. An `apply` block that implements the control logic to invoke the two
    tables.
 
1. A deparser that emits headers in the proper order.
     
To keep the exercise simple, we will ignore the `ipv4_checksum`. You should not
need any control plane rules for this exercise.

## Step 3: Run your solution

Follow the instructions from Step 1.  This time, you should be able to
successfully `ping` the switch.

### Troubleshooting

There are several ways that problems might manifest:

1. `arp.p4` fails to compile.  In this case, `run.sh` will report the
error emitted from the compiler and stop.

1. `arp.p4` compiles, but the switch does not process packets in the desired
way.  The `build/logs/<switch-name>.log` files contain trace messages
describing how each switch processes each packet.  The output is detailed and
can help pinpoint logic errors in your implementation.

> Note that there are no control plane rules installed in this example, and so
> the `receive.py` and `send.py` scripts from the [IPv4
> Forwarding](../ipv4_forward) example will not work.

#### Cleaning up Mininet

In the latter case above, `run.sh` may leave a Mininet instance running in
the background.  Use the following command to clean up these instances:

```bash
mn -c
```

## Next Steps

Congratulations, your implementation works!  Move on to the next exercise:
turning your switch into a [Calculator](../calc).
