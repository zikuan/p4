# Load Balancing 

In this exercise, you will implement a form of load balancing based on
a single version of Equal-Cost Multipath Forwarding. The switch you
will implement will use two tables to forward packets to one of two
destination hosts at random. The first table will use a hash function
(applied to a 5-tuple consisting of the source and destination
Ethernet addresses, source and destination IP addresses, and IP
protocol) to select one of two hosts. The second table will use the
computed hash value to forward the packet to the selected host.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.

## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`load_balance.p4`, which initially drops all packets.  Your job (in
the next step) will be to extend it to properly forward packets.

Before that, let's compile the incomplete `load_balance.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   ./run.sh
   ```   
   This will:
   * compile `load_balance.p4`, and
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`) configured
     in a triangle, each connected to one host (`h1`, `h2`, `h3`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.2.2`, etc.  
   * We use the IP address 10.0.0.1 to indicate traffic that should be
     load balanced between `h2` and `h3`.

2. You should now see a Mininet command prompt.  Open three terminals
   for `h1`, `h2` and `h3`, respectively:
   ```bash
   mininet> xterm h1 h2 h3
   ```   
3. Each host includes a small Python-based messaging client and
   server.  In `h2` and `h3`'s XTerms, start the servers:
   ```bash
   ./receive.py
   ```
4. In `h1`'s XTerm, send a message from the client:
   ```bash
   ./send.py 10.0.0.1 "P4 is cool"
   ```
   The message will not be received.
5. Type `exit` to leave each XTerm and the Mininet command line.

The message was not received because each switch is programmed with
`load_balance.p4`, which drops all packets on arrival.  Your job is to
extend this file.

### A note about the control plane

P4 programs define a packet-processing pipeline, but the rules
governing packet processing are inserted into the pipeline by the
control plane.  When a rule matches a packet, its action is invoked
with parameters supplied by the control plane as part of the rule.

In this exercise, the control plane logic has already been
implemented.  As part of bringing up the Mininet instance, the
`run.sh` script will install packet-processing rules in the tables of
each switch.  These are defined in the `s1-commands.txt` file.

**Important:** A P4 program also defines the interface between the
switch pipeline and control plane. The `s1-commands.txt` file contains
a list of commands for the BMv2 switch API. These commands refer to
specific tables, keys, and actions by name, and any changes in the P4
program that add or rename tables, keys, or actions will need to be
reflected in these command files.

## Step 2: Implement Load Balancing

The `load_balance.p4` file contains a skeleton P4 program with key
pieces of logic replaced by `TODO` comments.  These should guide your
implementation---replace each `TODO` with logic implementing the
missing piece.

A complete `load_balance.p4` will contain the following components:

1. Header type definitions for Ethernet (`ethernet_t`) and IPv4 (`ipv4_t`).
2. Parsers for Ethernet and IPv4 that populate `ethernet_t` and `ipv4_t` fields.
3. An action to drop a packet, using `mark_to_drop()`.
4. **TODO:** An action (called `set_ecmp_select`), which will:
	1. Hashes the 5-tuple specified above using the `hash` extern
	2. Stores the result in the `meta.ecmp_select` field
5. **TODO:** A control that:
    1. Applies the `ecmp_group` table.
    2. Applies the `ecmp_nhop` table.
6. A deparser that selects the order in which fields inserted into the outgoing
   packet.
7. A `package` instantiation supplied with the parser, control, and deparser.
    > In general, a package also requires instances of checksum verification
    > and recomputation controls.  These are not necessary for this tutorial
    > and are replaced with instantiations of empty controls.

## Step 3: Run your solution

Follow the instructions from Step 1.  This time, your message from
`h1` should be delivered to `h2` or `h3`. If you send several
messages, some should be received by each server.

### Food for thought


### Troubleshooting

There are several ways that problems might manifest:

1. `load_balance.p4` fails to compile.  In this case, `run.sh` will
report the error emitted from the compiler and stop.

2. `load_balance.p4` compiles but does not support the control plane
rules in the `sX-commands.txt` files that `run.sh` tries to install
using the BMv2 CLI.  In this case, `run.sh` will report these errors
to `stderr`.  Use these error messages to fix your `load_balance.p4`
implementation.

3. `load_balance.p4` compiles, and the control plane rules are
installed, but the switch does not process packets in the desired way.
The `build/logs/<switch-name>.log` files contain trace messages
describing how each switch processes each packet.  The output is
detailed and can help pinpoint logic errors in your implementation.

#### Cleaning up Mininet

In the latter two cases above, `run.sh` may leave a Mininet instance
running in the background.  Use the following command to clean up
these instances:

```bash
mn -c
```

## Next Steps

Congratulations, your implementation works!  Move on to the next
exercise: [HULA](../hula).
