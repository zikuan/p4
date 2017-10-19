# Implementing basic forwarding with scrambled addresses

## Introduction

In this exercise, you will extend your solution to the basic
forwarding exercise with a new twist: switches will invert the bits
representing Ethernet and IPv4 address. Hence, in our triangle
topology, the packets in the interior of the network will have
unintelligble addresses.

> **Spoiler alert:** There is a reference solution in the `solution`
> sub-directory. Feel free to compare your implementation to the
> reference.

## Step 1: Run the (incomplete) starter code

The directory with this README also contains a skeleton P4 program,
`scrambler.p4`, which initially drops all packets. Your job (in the
next step) will be to extend it to properly forward IPv4 packets.

Before that, let's compile the incomplete `scrambler.p4` and bring
up a switch in Mininet to test its behavior.

1. In your shell, run:
   ```bash
   ./run.sh
   ```
   This will:
   * compile `scrambler.p4`, and
   * start a Mininet instance with three switches (`s1`, `s2`, `s3`) configured
     in a triangle, each connected to one host (`h1`, `h2`, `h3`).
   * The hosts are assigned IPs of `10.0.1.1`, `10.0.2.2`, etc.

2. You should now see a Mininet command prompt. Open two terminals
for `h1` and `h2`, respectively:
   ```bash
   mininet> xterm h1 h2
   ```
3. Each host includes a small Python-based messaging client and
server. In `h2`'s xterm, start the server:
   ```bash
   ./receive.py
   ```
4. In `h1`'s xterm, send a message from the client:
   ```bash
   ./send.py 10.0.2.2 "P4 is cool"
   ```
   The message will not be received.
5. Type `exit` to leave each xterm and the Mininet command line.

The message was not received because each switch is programmed with
`scrambler.p4`, which drops all packets on arrival. Your job is to
extend this file.

### A note about the control plane

P4 programs define a packet-processing pipeline, but the rules
governing packet processing are inserted into the pipeline by the
control plane. When a rule matches a packet, its action is invoked
with parameters supplied by the control plane as part of the rule.

In this exercise, the control plane logic has already been
implemented. As part of bringing up the Mininet instance, the
`run.sh` script will install packet-processing rules in the tables of
each switch. These are defined in the `sX-commands.txt` files, where
`X` corresponds to the switch number.

**Important:** A P4 program also defines the interface between the
switch pipeline and control plane. The `sX-commands.txt` files
contain lists of commands for the BMv2 switch API. These commands
refer to specific tables, keys, and actions by name, and any changes
in the P4 program that add or rename tables, keys, or actions will
need to be reflected in these command files.

## Step 2: Extend the basic forwarding solution to flip bits

The `scrambler.p4` file contains a skeleton P4 program in which one of
the actions has a `TODO` comment. These should guide your
implementation---replace the `TODO` with logic implementing the
missing piece.

A complete `scrambler.p4` will add an action `flip()` that inverts the
bits in the Ethernet and IPv4 headers. 

## Step 3: Run your solution

Follow the instructions from Step 1. This time, your message from
`h1` should be delivered to `h2`.

### Troubleshooting

There are several issues that might arise when developing your
solution:

1. `scrambler.p4` fails to compile. In this case, `run.sh` will
report the error emitted from the compiler and stop.

2. `scrambler.p4` compiles but does not support the control plane
rules in the `sX-commands.txt` files that `run.sh` tries to install
using the BMv2 CLI. In this case, `run.sh` will report these errors
to `stderr`. Use these error messages to fix your `scrambler.p4`
implementation.

3. `scrambler.p4` compiles, and the control plane rules are installed,
but the switch does not process packets in the desired way. The
`build/logs/<switch-name>.log` files contain trace messages describing
how each switch processes each packet. The output is detailed and can
help pinpoint logic errors in your implementation.

#### Cleaning up Mininet

In the latter two cases above, `run.sh` may leave a Mininet instance
running in the background. Use the following command to clean up
these instances:

```bash
mn -c
```

## Next Steps

Congratulations, your implementation works!  Move on to the next
exercise: implementing [Explicit Congestion Notification](../ecn).
