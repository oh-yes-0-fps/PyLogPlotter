import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datalogHandler as dlh
import random
import timeit

SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

LARGE_FILE = 'FRC_20221012_000713.wpilog'

LINE_TYPES = [float, int]

MARKER_TYPES = [str, bool]


def meta_sorter(data_entries:dict[str, dlh.entry_structure]):
    source_dct = {}
    can_dct = {}
    for entry in data_entries:
        src = data_entries[entry].metadata.get('source', None)
        source_dct[data_entries[entry].name] = src
        can = data_entries[entry].metadata.get('CAN', None)
        can_dct[data_entries[entry].name] = can
    return source_dct, can_dct

def plot(entry:str):
    e_struct = m_de[entry]

    try:
        if e_struct.dtype == list:
            etype = e_struct.data[0][0]
            print(e_struct.name)
        else:
            etype = e_struct.dtype
    except IndexError:
        etype = None
        e_struct.columns = ['empty']

    if etype in LINE_TYPES:
        display_mode = 'lines'
    elif etype in MARKER_TYPES:
        display_mode = 'markers'
    else:
        display_mode = 'lines+markers'

    graph = go.Figure()

    if len(e_struct.columns) == 1:
        graph.add_trace(go.Scatter(x=e_struct.index, y=e_struct.data, mode= display_mode, showlegend=True))
    else:
        for i in range(len(e_struct.columns)):
            trace_lst = []
            for j in e_struct.data:
                trace_lst.append(j[i])
            graph.add_trace(go.Scatter(x=e_struct.index, y=e_struct.data[i], name=e_struct.columns[i], mode= display_mode, showlegend=True))

    if e_struct.dtype == list:
        graph.update_layout(title_text=f"{','.join(e_struct.columns)} vs Time", xaxis_title="Time", yaxis_title=f"{','.join(e_struct.columns)}")
    else:
        graph.update_layout(title_text=f"{e_struct.name} vs Time", xaxis_title="Time", yaxis_title=f"{e_struct.name}", )

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



if __name__ == '__main__':
    entries:list[str] = []
    log = dlh.DatalogHandler(LARGE_FILE)
    m_de:dict[str, dlh.entry_structure] = log.data_entries
    for i in m_de:
        plot(i)
    # source_dct, can_dct = meta_sorter(m_de)
    # for i in source_dct:
    #         plot(i)
