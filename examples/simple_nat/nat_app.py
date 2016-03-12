# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from scapy.all import *
import subprocess
import os

CLI_PATH = None

EXTERN_IP = "192.168.0.1"

current_nat_port = 1025
nat_mappings = {}

def send_to_CLI(cmd):
    this_dir = os.path.dirname(os.path.realpath(__file__))
    p = Popen(os.path.join(this_dir, 'sswitch_CLI.sh'), stdout=PIPE, stdin=PIPE)
    output = p.communicate(input=cmd)[0]
    # print output

# This is a very basic implementation of a full-cone NAT for TCP traffic
# We do not maintain a state machine for each connection, so we are not able to
# cleanup the port mappings, but this is sufficient for demonstration purposes
def process_cpu_pkt(p):
    global current_nat_port
    global EXTERN_IP

    p_str = str(p)
    # 0-7  : preamble
    # 8    : device
    # 9    : reason
    # 10   : iface
    # 11-  : data packet (TCP)
    if p_str[:8] != '\x00' * 8 or p_str[8] != '\x00' or p_str[9] != '\xab':
        return
    ip_hdr = None
    tcp_hdr = None
    try:
        p2 = Ether(p_str[11:])
        ip_hdr = p2['IP']
        tcp_hdr = p2['TCP']
    except:
        return
    print "Packet received"
    print p2.summary()
    if (ip_hdr.src, tcp_hdr.sport) not in nat_mappings:
        ext_port = current_nat_port
        current_nat_port += 1
        print "Allocating external port", ext_port
        nat_mappings[(ip_hdr.src, tcp_hdr.sport)] = ext_port
        # internal to external rule for this mapping
        send_to_CLI("table_add nat nat_hit_int_to_ext 0 1 1 %s&&&255.255.255.255 0.0.0.0&&&0.0.0.0 %d&&&0xffff 0&&&0 => %s %d 1" %\
                    (ip_hdr.src, tcp_hdr.sport, EXTERN_IP, ext_port))
        # external to internal rule for this mapping
        send_to_CLI("table_add nat nat_hit_ext_to_int 1 1 1 0.0.0.0&&&0.0.0.0 %s&&&255.255.255.255 0&&&0 %d&&&0xffff => %s %d 1" %\
                    (EXTERN_IP, ext_port, ip_hdr.src, tcp_hdr.sport))
    # a little bit hacky, this essentially ensures that the packet we re-inject
    # in the CPU iface will not be processed again by this method
    new_p = p_str[:9] + '\xac' + p_str[10:]
    sendp(new_p, iface="cpu-veth-0", verbose=0)

def main():
    sniff(iface="cpu-veth-0", prn=lambda x: process_cpu_pkt(x))

if __name__ == '__main__':
    main()
