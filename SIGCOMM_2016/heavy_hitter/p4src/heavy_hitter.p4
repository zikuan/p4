/* Copyright 2013-present Barefoot Networks, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#define HEAVY_HITTER_THRESHOLD 1000

header_type ethernet_t {
    fields {
        dstAddr : 48;
        srcAddr : 48;
        etherType : 16;
    }
}

header_type ipv4_t {
    fields {
        version : 4;
        ihl : 4;
        diffserv : 8;
        totalLen : 16;
        identification : 16;
        flags : 3;
        fragOffset : 13;
        ttl : 8;
        protocol : 8;
        hdrChecksum : 16;
        srcAddr : 32;
        dstAddr: 32;
    }
}

parser start {
    return parse_ethernet;
}

#define ETHERTYPE_IPV4 0x0800

header ethernet_t ethernet;

parser parse_ethernet {
    extract(ethernet);
    return select(latest.etherType) {
        ETHERTYPE_IPV4 : parse_ipv4;
        default: ingress;
    }
}

header ipv4_t ipv4;

field_list ipv4_checksum_list {
        ipv4.version;
        ipv4.ihl;
        ipv4.diffserv;
        ipv4.totalLen;
        ipv4.identification;
        ipv4.flags;
        ipv4.fragOffset;
        ipv4.ttl;
        ipv4.protocol;
        ipv4.srcAddr;
        ipv4.dstAddr;
}

field_list_calculation ipv4_checksum {
    input {
        ipv4_checksum_list;
    }
    algorithm : csum16;
    output_width : 16;
}

calculated_field ipv4.hdrChecksum  {
    verify ipv4_checksum;
    update ipv4_checksum;
}

parser parse_ipv4 {
    extract(ipv4);
    return ingress;
}

action _drop() {
    drop();
}

header_type custom_metadata_t {
    fields {
        nhop_ipv4: 32;
        // Add metadata for hashes
        hash_val1: 16;
        hash_val2: 16;
        count_val1: 16;
        count_val2: 16;
        is_heavy_hitter: 8;
    }
}

metadata custom_metadata_t custom_metadata;

action set_nhop(nhop_ipv4, port) {
    modify_field(custom_metadata.nhop_ipv4, nhop_ipv4);
    modify_field(standard_metadata.egress_spec, port);
    add_to_field(ipv4.ttl, -1);
}

action set_dmac(dmac) {
    modify_field(ethernet.dstAddr, dmac);
}

// Define the field list to compute the hash on
field_list ipv4_hash_fields {
    ipv4.srcAddr;
}

// Define two different hash functions to store the counts
field_list_calculation heavy_hitter_hash1 {
    input { 
        ipv4_hash_fields;
    }
    algorithm : csum16;
    output_width : 16;
}

field_list_calculation heavy_hitter_hash2 {
    input { 
        ipv4_hash_fields;
    }
    algorithm : crc16;
    output_width : 16;
}

// Define the registers to store the counts
register heavy_hitter_counter1{
    width : 16;
    instance_count : 16;
}

register heavy_hitter_counter2{
    width : 16;
    instance_count : 16;
}

// Actions to set heavy hitter filter
action set_heavy_hitter_count1() {
    modify_field_with_hash_based_offset(custom_metadata.hash_val1, 0,
                                        heavy_hitter_hash1, 16);
    register_read(custom_metadata.count_val1, heavy_hitter_counter1, custom_metadata.hash_val1);
    add_to_field(custom_metadata.count_val1, 1);
    register_write(heavy_hitter_counter1, custom_metadata.hash_val1, custom_metadata.count_val1);
}

action set_heavy_hitter_count2() {
    modify_field_with_hash_based_offset(custom_metadata.hash_val2, 0,
                                        heavy_hitter_hash2, 16);
    register_read(custom_metadata.count_val2, heavy_hitter_counter2, custom_metadata.hash_val2);
    add_to_field(custom_metadata.count_val2, 1);
    register_write(heavy_hitter_counter2, custom_metadata.hash_val2, custom_metadata.count_val2);
}

// Action to set the heavy hitter metadata indicator
action set_heavy_hitter() {
    modify_field(custom_metadata.is_heavy_hitter, 1);
}

// Define the tables to run actions
table set_heavy_hitter_count_table1 {
    actions { set_heavy_hitter_count1; }
    size: 1;
}

table set_heavy_hitter_count_table2 {
    actions { set_heavy_hitter_count2; }
    size: 1;
}

// Define table to set the heavy hitter metadata
table set_heavy_hitter_table {
    actions { set_heavy_hitter; }
    size: 1;
}

table ipv4_lpm {
    reads {
        ipv4.dstAddr : lpm;
    }
    actions {
        set_nhop;
        _drop;
    }
    size: 1024;
}

table forward {
    reads {
        custom_metadata.nhop_ipv4 : exact;
    }
    actions {
        set_dmac;
        _drop;
    }
    size: 512;
}

action rewrite_mac(smac) {
    modify_field(ethernet.srcAddr, smac);
}

table send_frame {
    reads {
        standard_metadata.egress_port: exact;
    }
    actions {
        rewrite_mac;
        _drop;
    }
    size: 256;
}

control ingress {
    apply(ipv4_lpm);
    // Add table control here
    apply(set_heavy_hitter_count_table1);
    apply(set_heavy_hitter_count_table2);
    if (custom_metadata.count_val1 > 1000 and custom_metadata.count_val2 > HEAVY_HITTER_THRESHOLD) {
        apply(set_heavy_hitter_table);
    }
    apply(forward);
}

control egress {
    apply(send_frame);
}
