import datalogHandler as dlh

SMALL_FILE = 'FRC_20221022_150128_NYROC_Q17.wpilog'

if __name__ == '__main__':
    entries:list[str] = []
    log = dlh.DatalogHandler(SMALL_FILE)
    # m_de:dict[str, dlh.entry_structure] = log.data_entries
    for i in log:
        print(i)

