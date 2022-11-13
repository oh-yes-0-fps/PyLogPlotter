import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datalogHandler as dlh


SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

LARGE_FILE = 'FRC_20221012_000713.wpilog'

LINE_TYPES = [float, int]

MARKER_TYPES = [str, bool]


# def meta_sorter(data_entries:dict[str, dlh.entry_structure]):
#     source_dct = {}
#     can_dct = {}
#     for entry in data_entries:
#         src = data_entries[entry].metadata.get('source', None)
#         source_dct[data_entries[entry].name] = src
#         can = data_entries[entry].metadata.get('CAN', None)
#         can_dct[data_entries[entry].name] = can
#     return source_dct, can_dct

def plot(traces:list[dlh.trace_structure], name:str):

    graph = go.Figure() #GET IT, GOFIGURE!!!!!!!!!


    for trace in traces:
        if trace == True:
            graph.add_trace(go.Scatter(x=trace.timestamps, y=trace.data, mode= mode(trace.type), showlegend=True, name=trace.name))

    graph.update_layout(xaxis_title="Time", yaxis_title=f"Data", )#title_text=f"{e_struct.name} vs Time", 

    # Add range slider
    graph.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="-"
        )
    )

    graph.show()

def mode(_type:type):
    if _type in LINE_TYPES:
        return 'lines'
    elif _type in MARKER_TYPES:
        return 'markers'
    else:
        return 'lines+markers'

NUM_TO_SHOW = 10

import random

if __name__ == '__main__':
    logs_shown = 0
    log = dlh.DatalogHandler(LARGE_FILE)
    for trace in log:
        trace = [trace] #type: ignore
        trace:list[dlh.trace_structure]  #just type annotation
        if random.randint(0, 100) < 11:
            plot(trace, "NAME")
            logs_shown += 1
        if logs_shown >= NUM_TO_SHOW:
            break

