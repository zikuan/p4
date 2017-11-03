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
from abc import abstractmethod

import grpc
from p4 import p4runtime_pb2
from p4.tmp import p4config_pb2

from p4info import p4browser


def buildSetPipelineRequest(p4info, device_config, device_id):
    request = p4runtime_pb2.SetForwardingPipelineConfigRequest()
    config = request.configs.add()
    config.device_id = device_id
    config.p4info.CopyFrom(p4info)
    config.p4_device_config = device_config.SerializeToString()
    request.action = p4runtime_pb2.SetForwardingPipelineConfigRequest.VERIFY_AND_COMMIT
    return request


def buildTableEntry(p4info_browser,
                    table_name,
                    match_fields={},
                    action_name=None,
                    action_params={}):
    table_entry = p4runtime_pb2.TableEntry()
    table_entry.table_id = p4info_browser.get_tables_id(table_name)
    if match_fields:
        table_entry.match.extend([
            p4info_browser.get_match_field_pb(table_name, match_field_name, value)
            for match_field_name, value in match_fields.iteritems()
        ])
    if action_name:
        action = table_entry.action.action
        action.action_id = p4info_browser.get_actions_id(action_name)
        if action_params:
            action.params.extend([
                p4info_browser.get_action_param_pb(action_name, field_name, value)
                for field_name, value in action_params.iteritems()
            ])
    return table_entry


class SwitchConnection(object):
    def __init__(self, name, address='127.0.0.1:50051', device_id=0):
        self.name = name
        self.address = address
        self.device_id = device_id
        self.p4info = None
        self.channel = grpc.insecure_channel(self.address)
        # TODO Do want to do a better job managing stub?
        self.client_stub = p4runtime_pb2.P4RuntimeStub(self.channel)

    @abstractmethod
    def buildDeviceConfig(self, **kwargs):
        return p4config_pb2.P4DeviceConfig()

    def SetForwardingPipelineConfig(self, p4info_file_path, dry_run=False, **kwargs):
        p4info_broswer = p4browser.P4InfoBrowser(p4info_file_path)
        device_config = self.buildDeviceConfig(**kwargs)
        request = buildSetPipelineRequest(p4info_broswer.p4info, device_config, self.device_id)
        if dry_run:
            print "P4 Runtime SetForwardingPipelineConfig:", request
        else:
            self.client_stub.SetForwardingPipelineConfig(request)
        # Update the local P4 Info reference
        self.p4info_broswer = p4info_broswer

    def buildTableEntry(self,
                        table_name,
                        match_fields={},
                        action_name=None,
                        action_params={}):
        return buildTableEntry(self.p4info_broswer, table_name, match_fields, action_name, action_params)

    def WriteTableEntry(self, table_entry, dry_run=False):
        request = p4runtime_pb2.WriteRequest()
        request.device_id = self.device_id
        update = request.updates.add()
        update.type = p4runtime_pb2.Update.INSERT
        update.entity.table_entry.CopyFrom(table_entry)
        if dry_run:
            print "P4 Runtime Write:", request
        else:
            print self.client_stub.Write(request)

    def ReadTableEntries(self, table_name, dry_run=False):
        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.device_id
        entity = request.entities.add()
        table_entry = entity.table_entry
        table_entry.table_id = self.p4info_broswer.get_tables_id(table_name)
        if dry_run:
            print "P4 Runtime Read:", request
        else:
            for response in self.client_stub.Read(request):
                yield response

    def ReadDirectCounters(self, table_name=None, counter_name=None, table_entry=None, dry_run=False):
        request = p4runtime_pb2.ReadRequest()
        request.device_id = self.device_id
        entity = request.entities.add()
        counter_entry = entity.direct_counter_entry
        if counter_name:
            counter_entry.counter_id = self.p4info_broswer.get_direct_counters_id(counter_name)
        else:
            counter_entry.counter_id = 0
        # TODO we may not need this table entry
        if table_name:
            table_entry.table_id = self.p4info_broswer.get_tables_id(table_name)
            counter_entry.table_entry.CopyFrom(table_entry)
        counter_entry.data.packet_count = 0
        if dry_run:
            print "P4 Runtime Read:", request
        else:
            for response in self.client_stub.Read(request):
                print response
