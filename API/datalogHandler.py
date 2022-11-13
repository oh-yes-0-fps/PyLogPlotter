import API.datalog as dl
from datetime import datetime
import mmap
# import sys
from typing import Any, Union, Optional
from types import NoneType
import re

REPR_METADATA = True

class trace_structure:
    """
    An easily mutable representation of the data needed for a\n
    plotly graph trace, with a name, data, and timestamps for data.
    """

    def __init__(self, _name:str, _type:type, _metadata:dict[str, list]):
        self.name = _name
        self.type = _type
        self.metadata = _metadata

        self.data = []
        self.timestamps = []

    def __repr__(self):
        if REPR_METADATA:
            return f"trace_structure({self.name}, {self.type}, {self.metadata})"
        else:
            return f"trace_structure {self.name} -> {self.type} with {len(self.data)} entries)"

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, trace_structure):
            return self.name == __o.name
        elif isinstance(__o, bool):
            if self.data:
                return True
            else:
                return False
        else:
            return False

    def trace_append(self, value:object, timestamp:float):
        if value:
            self.data.append(value)
            self.timestamps.append(timestamp)


class entry_manager:
    """
    A class to hold and manage the traces of a given entry.\n
    A list entry will produce multipl traces
    """

    def __init__(self, _name:str, _type:tuple[type, Optional[type]], _metaData:str) -> None:
        self.name = _name
        self.type = _type
        self.metaData = self.metadata_parser(_metaData)

        self.traces:list[trace_structure] = []

        self.bHasBeenAbandoned:bool = False

    def metadata_parser(self, __metadata:str):
        """turns a string of metadata into a dictionary with taking format\n
        of key:value or key:value,value,value\n
        key is always in uppercase"""
        __metadata = __metadata.replace('\",\"', '|')
        meta_lst = __metadata.split('|')
        meta_dct:dict[str, list[Union[str, int]]] = {}
        pos_pattern = re.compile(r'(\w+):(\w+)')
        neg_pattern = re.compile(r'(\"|\}|\{)')
        for md in meta_lst:
            md = re.sub(neg_pattern, '', md)
            match = pos_pattern.match(md)
            if match:
                md_key:str = str(match.group(1)).upper()
                md_value:list[str] = [match.group(2)]
                if ',' in md_value[0]:
                    md_value:list[str] = md_value[0].split(',')
                meta_dct[md_key] = md_value #type:ignore
        return meta_dct

    def construct_traces(self, traces:int) -> None:
        #i don't like how many for loops im doing but i dont know how to do it better
        for i in range(traces):
            names = self.metaData.get('NAMES', None)
            if (not names or len(names) != traces) and traces > 1:
                self.traces.append(trace_structure(f'{self.name}_{i}', self.type[0], self.metaData))
            else:
                self.traces.append(trace_structure(self.name, self.type[0], self.metaData))

    def add(self, value:object, timestamp:float) -> None:
        if self.bHasBeenAbandoned:return #if its an array that has varying entry lenghts im just gonna ignore it
        if not self.traces:
            if isinstance(value, list):
                self.metaData['ARRAY'] = [self.name]
                self.construct_traces(len(value))
            else:
                self.construct_traces(1)
        if isinstance(value, list):
            if len(value) != len(self.traces):
                self.bHasBeenAbandoned = True
                print(f'Abandoned: {self.name} containing {self.traces[0].data}')
                self.traces = []
                return
            for i in range(len(value)):
                self.traces[i].trace_append(value[i], timestamp)
        else:
            self.traces[0].trace_append(value, timestamp)



class DatalogHandler:
    def __init__(self, filename: str):
        self.data_entries:dict[str, entry_manager] = {}
        #---------File Extraction and Verification--------#
        with open(filename, "r") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self.reader = dl.DataLogReader(mm) #type: ignore
            if not self.reader:
                print("not a log file")
                exit(1)
        self.parse_datalog()


    def parse_datalog(self):

        raw_entries = 0

        sys_time_calls = 0

        #---------Data Extraction--------#
        f_entries:dict[int, dl.StartRecordData] = {}
        for record in self.reader:
            timestamp = record.timestamp
            if record.isStart():
                try:
                    data = record.getStartData()
                    # print(data.metadata)
                    f_entries[data.entry] = data
                    self.data_entries[data.name] = entry_manager(data.name, get_type(data.type), data.metadata)
                except TypeError as e:
                    print("Error: ", e)
            elif record.isFinish():
                try:
                    entry = record.getFinishEntry()
                    try:
                        del f_entries[entry]
                    except KeyError:
                        pass
                except TypeError as e:
                    print("Error: ", e)
            elif record.isSetMetadata():
                try:
                    data = record.getSetMetadataData()
                    print(f"SetMetadata({data.entry}, '{data.metadata}') [{timestamp}]")
                except TypeError as e:
                    print("SetMetadata(INVALID)")
            elif record.isControl():
                pass
            else:
                entry = f_entries.get(record.entry, None)
                if entry is None:
                    continue
                try:
                    # handle systemTime specially
                    # every 5 seconds robot should send a systemTime record
                    if entry.name == "systemTime" and entry.type == "int64":
                        sys_time_calls += 1
                        continue
                    if entry.type == "double":
                        value = record.getDouble()
                    elif entry.type == "int64":
                        value = record.getInteger()
                    elif entry.type == "string" or entry.type == "json":
                        value = record.getString()
                    elif entry.type == "boolean":
                        value = record.getBoolean()
                    elif entry.type == "boolean[]":
                        value = record.getBooleanArray()
                    elif entry.type == "double[]":
                        value = record.getDoubleArray().tolist()
                    elif entry.type == "float[]":
                        value = record.getFloatArray().tolist()
                    elif entry.type == "int64[]":
                        value = record.getIntegerArray().tolist()
                    elif entry.type == "string[]":
                        value = record.getStringArray()
                    else:
                        if entry.type == 'raw':
                            raw_entries += 1
                            continue
                        print(f'Unknown type:{entry.name} -> {entry.type}')
                        continue
                    self.data_entries[entry.name].add(value, timestamp)
                except TypeError as e:
                    print("Error: ", e)
        print(f"Duration of log: {sys_time_calls*5} seconds")
        if raw_entries:
            print(f"Unparsed Raw entries: {raw_entries}")

    def __iter__(self):
        all_traces = []
        for i in self.data_entries.values():
            all_traces.extend(i.traces)
        return iter(all_traces)

def get_type(type_string:str) -> tuple[type, Optional[type]]:
    if type_string == 'double':
        return (float, None)
    elif type_string == 'int64':
        return (int, None)
    elif type_string == 'string':
        return (str, None)
    elif type_string == 'json':
        return (str, None)
    elif type_string == 'boolean':
        return (bool, None)
    elif type_string == 'boolean[]':
        return (bool, list)
    elif type_string == 'double[]':
        return (float, list)
    elif type_string == 'float[]':
        return (float, list)
    elif type_string == 'int64[]':
        return (int, list)
    elif type_string == 'string[]':
        return (str, list)
    else:
        return (NoneType, None)