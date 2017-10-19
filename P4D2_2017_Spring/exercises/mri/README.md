# Implementing MRI

## Introduction

The objective of this tutorial is to extend basic L3 forwarding with a
scaled-down version of In-Band Network Telemetry (INT), which we call
Multi-Hop Route Inspection (MRI).

MRI allows users to track the path that every packet travels through
the network. To support this functionality, you will need to write a
P4 program that appends an ID to the header stack of every packet. At
the destination, the sequence of switch IDs correspond to the path.

As before, we have already defined the control plane rules, so you
only need to implement the data plane logic of your P4 program.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the reference.

## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`mri.p4`, which initially implements L3 forwarding.  Your job (in the
next step) will be to extend it to properly append the MRI custom
headers.

Before that, let's compile the incomplete `mri.p4` and bring up a
switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   ./run.sh
   ```
   This will:
   * compile `mri.p4`, and
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
   The message "P4 is cool" should be received in `h2`'s xterm,
5. Type `exit` to leave each xterm and the Mininet command line.

You should see the message received at host `h2`, but without any information
about the path the message took.  Your job is to extend the code in `mri.p4` to
implement the MRI logic to record the path.


### A note about the control plane

P4 programs define a packet-processing pipeline, but the rules governing packet
processing are inserted into the pipeline by the control plane.  When a rule
matches a packet, its action is invoked with parameters supplied by the control
plane as part of the rule.

In this exercise, the control plane logic has already been implemented.  As
part of bringing up the Mininet instance, the `run.sh` script will install
packet-processing rules in the tables of each switch.  These are defined in the
`sX-commands.txt` files, where `X` corresponds to the switch number.


## Step 2: Implement MRI


The `mri.p4` file contains a skeleton P4 program with key pieces of
logic replaced by `TODO` comments.  These should guide your
implementation---replace each `TODO` with logic implementing the missing piece.

MRI will require two custom headers. The first header, `mri_t`,
contains a single field `count`, which indicates the number of switch
IDs that follow. The second header, `switch_t`, contains a single
field with the switch ID. 

One of the biggest challenges in implementing MRI is handling the
recursive logic for parsing these two headers. We will use a
`parser_metadata` field, `remaining`, to keep track of how many
`switch_t` headers we need to parse.  In the `parse_mri` state, this
field should be set to `hdr.mri.count`.  In the `parse_swid` state,
this field should be decremented. The `parse_swid` state will
transition to itself until `remaining` is 0.

The MRI custom headers will be carried inside an IP Options
header. The IP Options header contains a field, `option`, which
indicates the type of the option. We will use a special type 31 to
indicate the presence of the MRI headers.

Beyond the parser logic, you will add a table, `swid` to store the
switch ID, and actions that add the `mri_t` header if it doesn't
exist, increment the `count` field, and append a `switch_t` header.


A complete `mri.p4` will contain the following components:


1. Header type definitions for Ethernet (`ethernet_t`), IPv4 (`ipv4_t`),
   IP Options (`ipv4_option_t`), MRI (`mri_t`), and Switch (`switch_t`). 
2. Parsers for Ethernet, IPv4, IP Options, MRI, and Switch that will
populate `ethernet_t`, `ipv4_t`, `ipv4_option_t`, `mri_t`, and
`switch_t`.
3. An action to drop a packet, using `mark_to_drop()`.
4. An action (called `ipv4_forward`), which will:
	1. Set the egress port for the next hop. 
	2. Update the ethernet destination address with the address of the next hop. 
	3. Update the ethernet source address with the address of the switch. 
	4. Decrement the TTL.
5. An action (called `add_mri_option`) that will add the IP Options and MRI
header. Note that you can use the `setValid()` function, which adds a
header if it does not exist, but otherwise leaves the packet
unmodified.
6. An action (called `add_swid`) that will add the switch ID header.
7. A table (`swid`) to store the switch ID, and calls `add_swid`. 
8. A control that:
    1. Defines a table that will read an IPv4 destination address, and
       invoke either `drop` or `ipv4_forward`.
    1. An `apply` block that applies the table.
9. A deparser that selects the order in which fields inserted into the outgoing
   packet.
10. A `package` instantiation supplied with the parser, control, and deparser.
    
    > In general, a package also requires instances of checksum verification
    > and recomputation controls.  These are not necessary for this tutorial
    > and are replaced with instantiations of empty controls.


## Step 3: Run your solution

Follow the instructions from Step 1.  This time, when your message from `h1` is
 delivered to `h2`, you should see the seqeunce of switches
through which the packet traveled. The expected output will look like the
following, which shows the MRI header, with a `count` of 2, and switch ids (`swids`) 2 and 1.

```

got a packet
###[ Ethernet ]###
  dst       = 00:aa:00:02:00:02
  src       = f2:ed:e6:df:4e:fa
  type      = 0x800
###[ IP ]###
     version   = 4L
     ihl       = 8L
     tos       = 0x0
     len       = 33
     id        = 1
     flags     =
     frag      = 0L
     ttl       = 62
     proto     = udp
     chksum    = 0x63b8
     src       = 10.0.1.10
     dst       = 10.0.2.10
     \options   \
      |###[ MRI ]###
      |  copy_flag = 1L
      |  optclass  = debug
      |  option    = 31L
      |  length    = 12
      |  count     = 2
      |  swids     = [2, 1]
```

### Troubleshooting

There are several ways that problems might manifest:

1. `mri.p4` fails to compile.  In this case, `run.sh` will report the
error emitted from the compiler and stop.

1. `mri.p4` compiles but does not support the control plane rules in
the `sX-commands.txt` files that `run.sh` tries to install using the BMv2 CLI.
In this case, `run.sh` will report these errors to `stderr`.  Use these error
messages to fix your `ipv4_forward.p4` implementation.

1. `mri.p4` compiles, and the control plane rules are installed, but
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
implementing an [ARP and ICMP Responder](../arp).



