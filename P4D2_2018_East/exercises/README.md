# P4 Tutorial

## Introduction

Welcome to the P4 Tutorial!

We've prepared a set of exercises to help you get started with P4
programming, organized into four modules:

1. Introduction and Language Basics
* [Basic Forwarding](./basic)
* [Basic Tunneling](./basic_tunnel)

2. P4 Runtime and the Control Plane
* [P4 Runtime](./p4runtime)

3. Monitoring and Debugging
* [Explicit Congestion Notification](./ecn)
* [Multi-Hop Route Inspection](./mri)

4. Advanced Data Structures
* [Source Routing](./source_routing)
* [Calculator](./calc)

5. Dynamic Behavior
* [Load Balancing](./load_balance)

## Obtaining required software

If you are starting this tutorial at the Fall 2017 P4 Developer Day, then we've already
provided you with a virtual machine that has all of the required
software installed.

Otherwise, to complete the exercises, you will need to either build a
virtual machine or install several dependencies.

To build the virtual machine:
- Install [Vagrant](https://vagrantup.com) and [VirtualBox](https://virtualbox.org)
- `cd vm`
- `vagrant up`
- Log in with username `p4` and password `p4` and issue the command `sudo shutdown -r now`
- When the machine reboots, you should have a graphical desktop machine with the required
software pre-installed.

To install dependencies by hand, please reference the [vm](../vm) installation scripts.
They contain the dependencies, versions, and installation procedure.
You can run them directly on an Ubuntu 16.04 machine:
- `sudo ./root-bootstrap.sh`
- `sudo ./user-bootstrap.sh`
