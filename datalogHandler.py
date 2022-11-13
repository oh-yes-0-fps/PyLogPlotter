import pandas as pd #we love native code😖
import datalog as dl
from datetime import datetime
import mmap
import sys
import re
import timeit

TIMESTAMP_DENOMINATOR = 1000000

class entry_structure:
    """
    An easily mutable representation of the data needed for a\n
    pandas DataFrame, can be converted to a DataFrame with to_dataframe()
    """
    def __init__(self, name:str, type:str, metadata:str):
        self.data = []
        self.index = []
        self.name = name
        self.columns = [name]
        self.dtype = type
        self.metadata = metadata
        self.metadata_parser()
        # self.type_str_to_type()


    def metadata_parser(self):
        meta_lst = self.metadata.split('|')
        meta_dct = {}
        pattern = re.compile(r'(\w+):(\w+)')
        for meta in meta_lst:
            match = pattern.match(meta)
            if match:
                meta_dct[match.group(1)] = match.group(2)
        if 'NAMES' in meta_dct:
            self.columns = meta_dct['NAMES'].split(',')
            del meta_dct['NAMES']
        self.metadata = meta_dct

    # def type_str_to_type(self):
    #     if self.dtype == 'int64':
    #         self.dtype = int
    #     elif self.dtype == 'float':
    #         self.dtype = float
    #     elif self.dtype == 'string':
    #         self.dtype = str
    #     elif self.dtype == 'boolean':
    #         self.dtype = bool
    #     elif self.dtype == 'double':
    #         self.dtype = float
    #     elif '[]' in self.dtype:
    #         self.dtype = list
    #     else:
    #         self.dtype = None

    def __repr__(self) -> str:
        return f'{self.name} :: {self.dtype} :: {self.metadata}'

    def add(self, value, timestamp):
        # if value is list create list with as many entries as len of value
        if isinstance(value, list):
            if len(self.columns) != len(value):
                self.columns = [self.name+'_UnNamed']*len(value)
        self.data.append(value)
        self.index.append(datetime.fromtimestamp(timestamp))
        # print(timestamp)



class DatalogHandler:
    def __init__(self, filename: str):
        self.data_entries:list[entry_structure] = []
        #---------File Extraction and Verification--------#
        with open(filename, "r") as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self.reader = dl.DataLogReader(mm)
            if not self.reader:
                print("not a log file", file=sys.stderr)
                sys.exit(1)
        self.parse_datalog()

    def parse_datalog(self):

        sys_time_calls = 0
        guide:dict[int, str] = {}

        #---------Data Extraction--------#
        f_entries:dict[str, dl.StartRecordData] = {}
        for record in self.reader:
            timestamp = record.timestamp
            if record.isStart():
                try:
                    data = record.getStartData()
                    f_entries[data.entry] = data
                    self.data_entries.insert(data.entry ,entry_structure(data.name, data.type, data.metadata))
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
                pass
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
                        dt = datetime.fromtimestamp(record.getInteger() / TIMESTAMP_DENOMINATOR)
                        sys_time_calls += 1
                        continue
                    if entry.type == "double":
                        value = record.getDouble()
                        # print(value)
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
                    self.data_entries[record.entry].add(value, timestamp)
                except TypeError as e:
                    print("Error: ", e)
        print(f"Duration of log: {sys_time_calls*5} seconds")

    def __iter__(self):
        return iter(self.data_entries)