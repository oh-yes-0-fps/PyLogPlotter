from datetime import datetime
import plotly.graph_objects as go
import API.datalogHandler as dlh
import sys
import json
import argparse


SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

LARGE_FILE = 'FRC_20221012_000713.wpilog'

LINE_TYPES = [float, int]

MARKER_TYPES = [str, bool]

class timeFixer:
    def __init__(self, timeOffset:float) -> None:
        self.timeOffset = timeOffset
    def __call__(self, timeList:list[float]):
        times:list[str] = list(map(self.timestapmToISO, timeList))
        # dt = datetime.fromtimestamp(times[0]).isoformat()
        # print("  {:%Y-%m-%d %H:%M:%S.%f}".format(dt))
        # print(times[0])
        # return np.array(times, dtype="datetime64[ms]")
        return times

    def timestapmToISO(self, _timestamp:float):
        timestamp = _timestamp - self.timeOffset
        dt = datetime.fromtimestamp(timestamp).isoformat()
        return dt

def plot(traces:list[dlh.trace_structure], name:str):

    graph = go.Figure() #GET IT, GOFIGURE!!!!!!!!!

    for trace in traces:
        if trace == True:
            graph.add_trace(go.Scatter(x=i_TimeFixer(trace.timestamps), y=trace.data, mode= mode(trace.type), showlegend=True, name=trace.name))

    graph.update_layout(title_text=f"{name} vs Time", xaxis_title="Time", yaxis_title=f"Data")

    # Add range slider
    graph.update_layout(
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            type="-"
        )
    )

    html_text = graph.to_html(full_html=True)
    #write html to file
    with open(f'.\\plots\\{name}.html', 'w') as f:
        f.write(html_text)

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
        jdata:dict[str,dict] = json.load(f)
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
    groupings = jdata['groupings']
    for group_name in groupings:
        #Making sets for faster sspeeds... not sure it really matters but why not
        trace_names = set(groupings[group_name]['trace_names'])
        array_names = groupings[group_name]['array_names']
        sources = groupings[group_name]['sources']
        groups[group_name] = []
        for trace in traces:
            if trace.type.__name__ in groupings[group_name]['blacklisted_types']:
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
    global i_TimeFixer
    i_TimeFixer = timeFixer(log.timeOffset)
    _groups, _can_id, _array_name = filter_traces(log, planner) #type: ignore
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
    parser.add_argument('-d', '--dump', help='A preliminary dump of the log file for data to use in gui, feed in name of robot')
    args = parser.parse_args()
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
