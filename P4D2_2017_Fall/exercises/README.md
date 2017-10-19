# P4 Tutorial

## Introduction

Welcome to the P4 Tutorial!

We've prepared a set of exercises to help you get started with P4
programming, organized into four modules:

1. Introduction
* [Basic Forwarding](./basic)
* [Scrambler](./scrambler)

2. Monitoring and Debugging
* [Explicit Congestion Notification](./ecn)
* [Multi-Hop Route Inspection](./mri)

3. Advanced Data Structures
* [Source Routing](./source_routing)
* [Calculator](./calc)

4. Dynamic Behavior
* [Load Balancing](./load_balance)
* [HULA](./hula)

## Obtaining required software

If you are starting this tutorial at SIGCOMM 2017, then we've already
provided you with a virtual machine that has all of the required
software installed.

Otherwise, to complete the exercises, you will need to either build a
virtual machine or install several dependencies.

To build the virtual machine:
- Install [Vagrant](https://vagrantup.com) and [VirtualBox](https://virtualbox.org)
- `cd vm`
- `vagrant up`
- Log in with username `p4` and password `p4` and issue the command `sudo shutdown -r now`
- When the machine reboots, you should have a graphical desktop machine with the required software pre-installed.

To install dependences by hand:
- `git clone https://github.com/p4lang/behavioral-model.git`
- `git clone https://github.com/p4lang/p4c`
- `git clone https://github.com/p4lang/tutorials`
Then follow the instructions for how to build each package. Each of
these repositories come with dependencies, which can be installed
using the supplied instructions. The first repository
([behavioral-model](https://github.com/p4lang/behavioral-model))
contains the P4 behavioral model. It is a C++ software switch that
will implement the functionality specified in your P4 program. The
second repository ([p4c](https://github.com/p4lang/p4c-bm)) is the
compiler for the behavioral model. It takes P4 program and produces a
JSON file which can be loaded by the behavioral model. The third
repository ([tutorial](https://github.com/p4lang/tutorial)) is the P4
Tutorial itself. You will also need to install `mininet`. On Ubuntu,
it would look like this:

```
$ sudo apt-get install mininet
```
