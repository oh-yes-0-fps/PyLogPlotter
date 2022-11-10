import pandas as pd #we love native code😖
import datalog as dl
from datetime import datetime
import mmap
import sys
import re

TIMESTAMP_DENOMINATOR = 1000000

class dataframe_entry:
    """
    An easily mutable representation of the data needed for a\n
    pandas DataFrame, can be converted to a DataFrame with to_dataframe()
    """
    def __init__(self, name:str, type:str, metadata:str):
        self.data = []
        self.index = []
        self.columns = [name]
        self.dtype = type
        self.metadata = metadata
        self.metadata_parser()
        self.type_str_to_type()


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

    def type_str_to_type(self):
        if self.dtype == 'int64':
            self.dtype = int
        elif self.dtype == 'float':
            self.dtype = float
        elif self.dtype == 'string':
            self.dtype = str
        elif self.dtype == 'boolean':
            self.dtype = bool
        elif self.dtype == 'double':
            self.dtype = float
        ##arrays
        elif self.dtype == 'int64[]':
            self.dtype = list[int]
        elif self.dtype == 'float[]':
            self.dtype = list[float]
        elif self.dtype == 'string[]':
            self.dtype = list[str]
        elif self.dtype == 'boolean[]':
            self.dtype = list[bool]
        elif self.dtype == 'double[]':
            self.dtype = list[float]
        else:
            self.dtype = None

    def add(self, value, timestamp):
        self.data.append(value)
        self.index.append(timestamp)

    def to_dataframe(self):
        return pd.DataFrame(self.data, index=self.index, columns=self.columns, dtype=self.dtype)


class DatalogHandler:
    def __init__(self, filename: str):
        self.data_entries:dict[str, dataframe_entry] = {}
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

        #---------Data Extraction--------#
        f_entries:dict[str, dl.StartRecordData] = {}
        for record in self.reader:
            timestamp = record.timestamp / TIMESTAMP_DENOMINATOR
            if record.isStart():
                try:
                    data = record.getStartData()
                    self.data_entries[data.name] = dataframe_entry(data.name, data.type, data.metadata)
                except TypeError as e:
                    print("Error: ", e)
            elif record.isFinish():
                try:
                    entry = record.getFinishEntry()
                    del f_entries[entry]
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
                    self.data_entries[entry.name].add(value, timestamp)
                except TypeError as e:
                    print("Error: ", e)
        print(f"Duration of log: {sys_time_calls*5} seconds")

    def __call__(self):
        pass