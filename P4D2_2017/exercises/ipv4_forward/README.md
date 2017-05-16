# Implementing L3 Forwarding

## Introduction

The objective of this tutorial is to implement basic L3 forwarding. To
keep the exercise small, we will just implement forwarding for IPv4.

With IPv4 forwarding, the switch must perform the following actions
for every packet: (i) update the source and destination MAC addresses,
(ii) decrement the time-to-live (TTL) in the IP header, and (iii)
forward the packet out the appropriate port.

Your switch will have a single table, which the control plane will
populate with static rules. Each rule will map an IP address to the
MAC address and output port for the next hop. We have already defined
the control plane rules, so you only need to implement the data plane
logic of your P4 program.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the reference.


## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`ipv4_forward.p4`, which initially drops all packets.  Your job (in the next
step) will be to extend it to properly forward IPv4 packets.

Before that, let's compile the incomplete `ip4v_forward.p4` and bring up a
switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   ./run.sh
   ```
   This will:
   * compile `ip4v_forward.p4`, and
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`) configured
     in a triangle, each connected to one host (`h1`, `h2`, `h3`).
   * The hosts are assigned IPs of `10.0.1.10`, `10.0.2.10`, etc.

2. You should now see a Mininet command prompt.  Open two terminals for `h1` and `h2`, respectively:
   ```bash
   mininet> xterm h1 h2
   ```
3. Each host includes a small Python-based messaging client and server.  In `h2`'s xterm, start the server:
   ```bash
   ./receive.py
   ```
4. In `h1`'s xterm, send a message from the client:
   ```bash
   ./send.py 10.0.2.10 "P4 is cool"
   ```
   The message will not be received.
5. Type `exit` to leave each xterm and the Mininet command line.

The message was not received because each switch is programmed with
`ip4v_forward.p4`, which drops all packets on arrival.  Your job is to extend
this file.

### A note about the control plane

P4 programs define a packet-processing pipeline, but the rules governing packet
processing are inserted into the pipeline by the control plane.  When a rule
matches a packet, its action is invoked with parameters supplied by the control
plane as part of the rule.

In this exercise, the control plane logic has already been implemented.  As
part of bringing up the Mininet instance, the `run.sh` script will install
packet-processing rules in the tables of each switch.  These are defined in the
`sX-commands.txt` files, where `X` corresponds to the switch number.

**Important:** A P4 program also defines the interface between the switch
pipeline and control plane.  The `sX-commands.txt` files contain lists of
commands for the BMv2 switch API. These commands refer to specific tables,
keys, and actions by name, and any changes in the P4 program that add or rename
tables, keys, or actions will need to be reflected in these command files.

## Step 2: Implement L3 forwarding

The `ipv4_forward.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments.  These should guide your
implementation---replace each `TODO` with logic implementing the missing piece.

A complete `ipv4_forward.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`) and IPv4 (`ipv4_t`).
2. **TODO:** Parsers for Ethernet and IPv4 that populate `ethernet_t` and `ipv4_t` fields.
3. An action to drop a packet, using `mark_to_drop()`.
4. **TODO:** An action (called `ipv4_forward`), which will:
	1. Set the egress port for the next hop. 
	2. Update the ethernet destination address with the address of the next hop. 
	3. Update the ethernet source address with the address of the switch. 
	4. Decrement the TTL.
5. **TODO:** A control that:
    1. Defines a table that will read an IPv4 destination address, and
       invoke either `drop` or `ipv4_forward`.
    1. An `apply` block that applies the table.
7. A deparser that selects the order in which fields inserted into the outgoing
   packet.
8. A `package` instantiation supplied with the parser, control, and deparser.
    > In general, a package also requires instances of checksum verification
    > and recomputation controls.  These are not necessary for this tutorial
    > and are replaced with instantiations of empty controls.

## Step 3: Run your solution

Follow the instructions from Step 1.  This time, your message from `h1` should
be delivered to `h2`.

### Food for thought

The "test suite" for your solution---sending a message from `h1` to `h2`---is
not very robust.  What else should you test to be confident of your
implementation?

> Although the Python `scapy` library is outside the scope of this tutorial,
> it can be used to generate packets for testing.  The `send.py` file shows how
> to use it.

Other questions to consider:

 - How would you enhance your program to support next hops?
 - Is this program enough to replace a router?  What's missing?

### Troubleshooting

There are several ways that problems might manifest:

1. `ipv4_forward.p4` fails to compile.  In this case, `run.sh` will report the
error emitted from the compiler and stop.

2. `ipv4_forward.p4` compiles but does not support the control plane rules in
the `sX-commands.txt` files that `run.sh` tries to install using the BMv2 CLI.
In this case, `run.sh` will report these errors to `stderr`.  Use these error
messages to fix your `ipv4_forward.p4` implementation.

3. `ipv4_forward.p4` compiles, and the control plane rules are installed, but
the switch does not process packets in the desired way.  The
`build/logs/<switch-name>.log` files contain trace messages describing how each
switch processes each packet.  The output is detailed and can help pinpoint
logic errors in your implementation.

#### Cleaning up Mininet

In the latter two cases above, `run.sh` may leave a Mininet instance running in
the background.  Use the following command to clean up these instances:

```bash
mn -c
```

## Next Steps

Congratulations, your implementation works!  Move on to the next exercise:
implementing basic network telemetry [Multi-Hop Route Inspection](../mri).
