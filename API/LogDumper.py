import API.datalogHandler as dlh
import json




def dump(fileReadName:str, fileWriteName:str):

    jdata = {
        'names': [],
        'sources': [],
        'canids': [],
        'arraynames': [],
    }

    log = dlh.DatalogHandler(fileReadName)
    for i in log:
        i:dlh.trace_structure
        jdata['names'].append(i.name)
        jdata['sources'].extend(i.metadata.get('SOURCE', []))
        jdata['arraynames'].extend(i.metadata.get('ARRAY', []))
    jdata['sources'] = list(set(jdata['sources']))
    jdata['arraynames'] = list(set(jdata['arraynames']))
    with open(f'.\\resources\\cached\\{fileWriteName}.json', 'w') as f:
        json.dump(jdata, f)

