#!/usr/bin/python

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

#
# Author: Brent Stephens 
#

from scapy.all import sniff, sendp
from scapy.all import Packet
from scapy.all import ShortField, IntField, LongField, BitField

import sys
import struct

def handle_pkt(pkt):
    pkt = str(pkt)
    if len(pkt) < 13: return
    preamble = pkt[:8]
    preamble_exp = "\x00" * 8
    if preamble != preamble_exp: return
    axonType = pkt[8]
    if axonType != "\x00": return
    axonLength = struct.unpack("!H", pkt[9:11])[0]
    fwdHopCount = struct.unpack("B", pkt[11])[0]
    revHopCount = struct.unpack("B", pkt[12])[0]
    if fwdHopCount != 0:
        print 'received a packet that has not been fully forwarded'
    if revHopCount <= 0:
        print 'received a packet that has no reverse hops'
    if axonLength != 2 + fwdHopCount + revHopCount:
        print 'received a packet with either an incorrect axonLength, fwdHopCount, or revHopCount'
    msg = pkt[11 + axonLength:]
    print msg
    sys.stdout.flush()

    # Optional debugging
    #print 'axonLength:', axonLength
    #print 'fwdHopCount:', fwdHopCount
    #print 'revHopCount:', revHopCount
    #print pkt

def main():
    sniff(iface = "eth0",
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
