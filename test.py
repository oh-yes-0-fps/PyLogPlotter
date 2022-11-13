from types import NoneType
import datalogHandler as dlh

SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

LARGE_FILE = 'FRC_20221012_000713.wpilog'

import time
import datetime

if __name__ == '__main__':
    log = dlh.DatalogHandler(SMALL_FILE)
    for i in log:
        print(i)


    pass

