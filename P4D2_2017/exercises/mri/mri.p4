/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<8>  UDP_PROTOCOL = 0x11;
const bit<16> TYPE_IPV4 = 0x800;
const bit<5>  IPV4_OPTION_MRI = 31;


#define MAX_HOPS 9

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> switchID_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header ipv4_option_t {
    bit<1> copyFlag;
    bit<2> optClass;
    bit<5> option;
    bit<8> optionLength;
}

header mri_t {
    bit<16>  count;
}

header switch_t {
    switchID_t  swid;
}

struct ingress_metadata_t {
    bit<16>  count;
}

struct parser_metadata_t {
    bit<16>  remaining;
}

struct metadata {
    ingress_metadata_t   ingress_metadata;
    parser_metadata_t   parser_metadata;
}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    ipv4_option_t  ipv4_option;
    mri_t        mri;
    switch_t[MAX_HOPS] swids;
}

error { IPHeaderTooShort }

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser ParserImpl(packet_in packet,
out headers hdr,
inout metadata meta,
inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        verify(hdr.ipv4.ihl >= 5, error.IPHeaderTooShort);
        /*
        * TODO: Modify the next line to select on the value of hdr.ipv4.ihl.
        * If the value of hdr.ipv4.ihl is set to 5, accept. 
        * Otherwise, transition to  parse_ipv4_option.
        */
        transition accept;
    }

    /* TODO: Implement the logic for parse_ipv4_options, parse_mri, and parse_swid */


    state parse_ipv4_option {
        /*
        * TODO: Add logic to:
        * - Extract the ipv4_option header.
        *   - If the value is equal to IPV4_OPTION_MRI, transition to parse_mri.
        *   - Otherwise, accept.
        */
    }

    state parse_mri {
        /*
        * TODO: Add logic to:
        * - Extract hdr.mri.
        * - Set meta.parser_metadata.remaining to hdr.mri.count
        * - Select on the value of meta.parser_metadata.remaining
        *   - If the value is equal to 0, accept.
        *   - Otherwise, transition to parse_swid.
        */
    }

    state parse_swid {
        /*
        * TODO: Add logic to:
        * - Extract hdr.swids.next.
        * - Decrement meta.parser_metadata.remaining by 1
        * - Select on the value of meta.parser_metadata.remaining
        *   - If the value is equal to 0, accept.
        *   - Otherwise, transition to parse_swid.
        */
    }    

}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control verifyChecksum(in headers hdr, inout metadata meta) {   
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop();
    }
    
    action add_mri_option() {
        /*
        * TODO: add logic to:
        * - Call setValid() on hdr.ipv4_option, which will add the header if it is not 
        *    there, or leave the packet unchanged.
        * - Set hdr.ipv4_option.copyFlag to 1
        * - Set hdr.ipv4_option.optClass to 2
        * - Set hdr.ipv4_option.option to IPV4_OPTION_MRI
        * - Set the hdr.ipv4_option.optionLength to 4 
        * - Call setValid() on hdr.mri
        * - Set hdr.mri.count to 0
        * - Increment hdr.ipv4.ihl by 1
        */
    }
    
    action add_swid(switchID_t id) {    

        /*
        * TODO: add logic to:
        - Increment hdr.mri.count by 1
        - Add a new swid header by calling push_front(1) on hdr.swids.
        - Set hdr.swids[0].swid to the id paremeter
        - Incremement hdr.ipv4.ihl by 1
        - Incrememtn hdr.ipv4_option.optionLength by 4
        */
    }
    
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table swid {
        actions =
        {
            /* TODO: repace NoAction with the correct action */
            NoAction;
        }
        /* TODO: set a default action. */
    }
    
    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = NoAction();
    }
    
    apply {

         ipv4_lpm.apply();

        /*
        * TODO: add logic to:
        * - If hdr.ipv4 is valid:
        *     - Apply table ipv4_lpm
        *     - If hdr.mri is not valid, call add_mri_option()
        *     - Apply table swid
        */
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/


control computeChecksum(
    inout headers  hdr,
    inout metadata meta)
{
    /* 
    * Ignore checksum for now. The reference solution contains a checksum
    * implementation. 
    */
    apply {  }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv4_option);
        packet.emit(hdr.mri);
        packet.emit(hdr.swids);                 
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
ParserImpl(),
verifyChecksum(),
ingress(),
egress(),
computeChecksum(),
DeparserImpl()
) main;
