# Copyright 2017-present Open Networking Foundation
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
import re

import google.protobuf.text_format
from p4 import p4runtime_pb2
from p4.config import p4info_pb2


class P4InfoBrowser(object):
    def __init__(self, p4_info_filepath):
        p4info = p4info_pb2.P4Info()
        # Load the p4info file into a skeleton P4Info object
        with open(p4_info_filepath) as p4info_f:
            google.protobuf.text_format.Merge(p4info_f.read(), p4info)
        self.p4info = p4info

    def get(self, entity_type, name=None, id=None):
        if name is not None and id is not None:
            raise AssertionError("name or id must be None")

        for o in getattr(self.p4info, entity_type):
            pre = o.preamble
            if name:
                if (pre.name == name or pre.alias == name):
                    return o
            else:
                if pre.id == id:
                    return o

        if name:
            raise AttributeError("Could not find %r of type %s" % (name, entity_type))
        else:
            raise AttributeError("Could not find id %r of type %s" % (id, entity_type))

    def get_id(self, entity_type, name):
        return self.get(entity_type, name=name).preamble.id

    def get_name(self, entity_type, id):
        return self.get(entity_type, id=id).preamble.name

    def get_alias(self, entity_type, id):
        return self.get(entity_type, id=id).preamble.alias

    def __getattr__(self, attr):
        # Synthesize convenience functions for name to id lookups for top-level entities
        # e.g. get_table_id() or get_action_id()
        m = re.search("^get_(\w+)_id$", attr)
        if m:
            primitive = m.group(1)
            return lambda name: self.get_id(primitive, name)

        # Synthesize convenience functions for id to name lookups
        m = re.search("^get_(\w+)_name$", attr)
        if m:
            primitive = m.group(1)
            return lambda id: self.get_name(primitive, id)

        raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))

    # TODO remove
    def get_table_entry(self, table_name):
        t = self.get(table_name, "table")
        entry = p4runtime_pb2.TableEntry()
        entry.table_id = t.preamble.id
        entry
        pass

    def get_match_field(self, table_name, match_field_name):
        for t in self.p4info.tables:
            pre = t.preamble
            if pre.name == table_name:
                for mf in t.match_fields:
                    if mf.name == match_field_name:
                        return mf

    def get_match_field_id(self, table_name, match_field_name):
        return self.get_match_field(table_name,match_field_name).id

    def get_match_field_pb(self, table_name, match_field_name, value):
        p4info_match = self.get_match_field(table_name, match_field_name)
        bw = p4info_match.bitwidth
        p4runtime_match = p4runtime_pb2.FieldMatch()
        p4runtime_match.field_id = p4info_match.id
        # TODO switch on match type and map the value into the appropriate message type
        match_type = p4info_pb2._MATCHFIELD_MATCHTYPE.values_by_number[
            p4info_match.match_type].name
        if match_type == 'EXACT':
            exact = p4runtime_match.exact
            exact.value = value
        elif match_type == 'LPM':
            lpm = p4runtime_match.lpm
            lpm.value = value[0]
            lpm.prefix_len = value[1]
        # TODO finish cases and validate types and bitwidth
        # VALID = 1;
        # EXACT = 2;
        # LPM = 3;
        # TERNARY = 4;
        # RANGE = 5;
        # and raise exception
        return p4runtime_match

    def get_action_param(self, action_name, param_name):
        for a in self.p4info.actions:
            pre = a.preamble
            if pre.name == action_name:
                for p in a.params:
                    if p.name == param_name:
                        return p
        raise AttributeError("%r has no attribute %r" % (action_name, param_name))


    def get_action_param_id(self, action_name, param_name):
        return self.get_action_param(action_name, param_name).id

    def get_action_param_pb(self, action_name, param_name, value):
        p4info_param = self.get_action_param(action_name, param_name)
        #bw = p4info_param.bitwidth
        p4runtime_param = p4runtime_pb2.Action.Param()
        p4runtime_param.param_id = p4info_param.id
        p4runtime_param.value = value # TODO make sure it's the correct bitwidth
        return p4runtime_param