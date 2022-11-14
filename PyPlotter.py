import plotly.graph_objects as go
import API.datalogHandler as dlh
import sys
import json
import argparse


SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

LARGE_FILE = 'FRC_20221012_000713.wpilog'

LINE_TYPES = [float, int]

MARKER_TYPES = [str, bool]

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

def filter_traces(traces:list[dlh.trace_structure], planner):
    planner = planner.removesuffix('.json').split('\\')[-1]
    with open(f'.\\resources\\{planner}.json', 'r') as f:
        jdata = json.load(f)
    can_id = {}
    array_name = {}
    gloabl_blacklist = set(jdata['settings']['global_blacklist'])
    groups = {}
    #gonna handle it in a few steps, def not the fastest way but should work for now
    for i in traces:
        if i.name in gloabl_blacklist:
            continue
        if jdata['settings']['auto_group_by_can']:
            can_id[i.metadata.get('CANID', '_')] = i
        if jdata['settings']['auto_group_by_array']:
            array_name[i.metadata.get('ARRAY', '_')] = i
    if '_' in array_name:
        del array_name['_']
    if '_' in can_id:
        del can_id['_']
    for group_name, Group_filter in enumerate(jdata['groupings']):
        #Making sets for faster sspeeds... not sure it really matters but why not
        trace_names = set(Group_filter['trace_names'])
        array_names = Group_filter['array_names']
        sources = Group_filter['sources']
        groups[group_name] = []
        for trace in traces:
            if trace.type.__name__ in Group_filter['blacklisted_types']:
                continue
            elif trace.name in jdata['settings']['global_blacklist']:
                continue
            elif trace.name in trace_names:
                groups[group_name].append(trace)
                continue
            elif any(source in trace.metadata.get('SOURCE', []) for source in sources):
                groups[group_name].append(trace)
                continue
            elif any(array_name in trace.metadata.get('ARRAY', []) for array_name in array_names):
                groups[group_name].append(trace)
                continue
    return groups, can_id, array_name
        
def plot_by_filename(filename:str, planner:str):
    log = dlh.DatalogHandler(sys.argv[1])
    _groups, _can_id, _array_name = filter_traces(log, planner)
    for i in _groups:
        plot(_groups[i], i)
    for i in _can_id:
        plot(_can_id[i], f'CANID: {i}')
    for i in _array_name:
        plot(_array_name[i], f'ARRAY: {i}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Plot a log file')
    # mut_group = parser.add_mutually_exclusive_group()
    parser.add_argument('filename', type=str, help='The file to plot')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p','--plot', action='store_true', help='The file to plot, needs -c aswell')
    group.add_argument('-g', '--gui', action='store_true', help='Run the config helper gui, needs -c aswell')
    parser.add_argument('-c', '--config', type=str, help='The json in resources to config the plots with', )
    parser.add_argument('-d', '--dump', type=None, help='A preliminary dump of the log file for data to use in gui, feed in name of robot')
    args = parser.parse_args()
    # if args.config:
    #     with open(args.config, 'r') as f:
    #         jdata = json.load(f)
    if args.dump:
        from API.LogDumper import dump
        dump(args.filename, args.dump)
    if args.gui:
        from API.PlotPlannerGUI import Main
        if args.config:
            Main(args.config)
        else:
            print('No config file specified, cannot  launch gui')
            exit(1)
    if args.plot:
        if args.config:
            plot_by_filename(args.filename, args.config)
        else:
            print('No config file specified, cannot plot')
            exit(1)
 