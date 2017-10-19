# P4 Tutorial

## Introduction

Welcome to the P4 Tutorial!

We've prepared a set of four exercises that will help you get started
with P4 programming:

1.  [L3 forwarding](./ipv4_forward)

2.  [Multi-Hop Route Inspection](./mri)

3.  [ARP/ICMP Responder](./arp)

4.  [Calculator](./calc)

## Obtaining required software

If you are starting this tutorial as part of the P4 Developer Day, then
we've already provided you with a virtual machine that has all of the
required software installed.

Otherwise, to complete the exercises, you will need to clone two p4lang Github repositories
and install their dependencies. To clonde the repositories:

- `git clone https://github.com/p4lang/behavioral-model.git bmv2`
- `git clone https://github.com/p4lang/p4c-bm.git p4c-bmv2`

The first repository ([bmv2](https://github.com/p4lang/behavioral-model)) is the
second version of the behavioral model. It is a C++ software switch that will
behave according to your P4 program. The second repository
([p4c-bmv2](https://github.com/p4lang/p4c-bm)) is the compiler for the
behavioral model: it takes P4 program and output a JSON file which can be loaded
by the behavioral model.

Each of these repositories come with dependencies. `p4c-bmv2` is a Python
repository and installing the required Python dependencies is very easy to do
using `pip`: `sudo pip install -r requirements.txt`.

`bmv2` is a C++ repository and has more external dependencies. They are listed
in the
[README](https://github.com/p4lang/behavioral-model/blob/master/README.md). If
you are running Ubuntu 14.04+, the dependencies should be easy to install (you
can use the `install_deps.sh` script that comes with `bmv2`). Do not forget to
build the code once all the dependencies have been installed:

```
$ ./autogen.sh
$ ./configure
$ make
```


You will also need to install `mininet`, as well as the following Python
packages: `scapy`, `thrift` (>= 0.9.2) and `networkx`. On Ubuntu, it would look
like this:

```
$ sudo apt-get install mininet
$ sudo pip install scapy thrift networkx
```

