import datalogHandler as dlh
import json


SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

LARGE_FILE = 'FRC_20221012_000713.wpilog'



if __name__ == '__main__':

    jdata = {
        'names': [],
        'sources': [],
        'canids': [],
        'arraynames': [],
    }

    log = dlh.DatalogHandler(SMALL_FILE)
    for i in log:
        i:dlh.trace_structure
        jdata['names'].append(i.name)
        jdata['sources'].extend(i.metadata.get('SOURCE', []))
        jdata['canids'].extend(i.metadata.get('CANID', []))
        jdata['arraynames'].extend(i.metadata.get('ARRAY', []))
    jdata['sources'] = list(set(jdata['sources']))
    jdata['canids'] = list(set(jdata['canids']))
    jdata['arraynames'] = list(set(jdata['arraynames']))
    file_name = SMALL_FILE.removesuffix('.wpilog')
    with open(f'.\\resources\\cached\\{file_name}.json', 'w') as f:
        json.dump(jdata, f)
    pass

