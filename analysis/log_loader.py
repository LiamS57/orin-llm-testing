# Helper script for loading a folder of logs for analysis.
# 
# Liam Seymour 6/26/24

#import pandas as pd
#import numpy as np
import os
import sys

sys.path.insert(0, '../tests')
from statlog import Log

class LogPeriod:
    name: str
    i: int
    length: float
    freq_gpu: list[tuple[float, float]]
    memory_ram: list[tuple[float, float]]
    memory_gpu: list[tuple[float, float]]
    power: list[tuple[float, float]]
    tokens_generated: int
    accuracy: float

class TaggedData:
    _tags: list[str]
    _periods: list[list[LogPeriod]]

    def has_tags(self, tags_to_check: list[str]) -> bool:
        for chk in tags_to_check:
            if chk not in self._tags:
                return False
        return True
    def period(self, period_name: str, iteration: int) -> LogPeriod:
        for plog in self._periods[iteration]:
            if plog.name == period_name:
                return plog
        return None
    
class TaggedDataList:
    _list: list[TaggedData]

    def with_tags(self, *tags) -> list[TaggedData]:
        return [tagged for tagged in self._list if tagged.has_tags(list(tags))]

def _get_timestamp_period(log: Log, flag: str) -> tuple[float, float]:
    start = log.get_timestamp(f'{flag}_START')
    end = log.get_timestamp(f'{flag}_END')
    if start == -1 or end == -1:
        return None, None
    return start, end


def load_logs_from_folder(in_folder: str) -> TaggedDataList:
    '''Loads log files from a given folder path.'''
    in_folder = os.path.abspath(in_folder)
    print('Loading all log files from', in_folder)

    # load from files into a list of logs associated with name fragments
    loaded: list[tuple[list[str], Log]] = list()
    num_loaded = 0
    for filename in os.listdir(in_folder):
        if filename.endswith('.json'):
            try:
                filepath = os.path.join(in_folder, filename)
                log_data = None
                with open(filepath, 'r') as fp:
                    jstr = ''.join(fp.readlines())
                    log_data = Log.from_json(jstr)
                
                name_data = filename[4:-5].split('_')
                #name_data.insert(0, name_data.pop()) # move suffix to the beginning of the name data

                loaded.append((name_data, log_data))
                num_loaded += 1
            except:
                pass
    print(f'Loaded {num_loaded} files')

    # move loaded data into tagged data
    tagged_data_list: list[TaggedData] = list()
    for name, log in sorted(loaded, key=lambda x: x[0]):
        i = int(name.pop(1)) # this fragment is an iteration number, the rest are used as tags

        period_names = list()
        for pname in [x.value[:-6] for x in log.timestamps if x.value.endswith('_START')]:
            if log.get_timestamp(f'{pname}_END') != -1:
                period_names.append(pname)
        
        period_list: list[LogPeriod] = list()
        for pname in period_names:
            # fill LogPeriod with data

            log_period = LogPeriod()
            log_period.name = pname
            log_period.i = i # TODO: REMOVE

            log_period.accuracy = log.accuracy
            log_period.tokens_generated = log.tokens_generated

            start, end = _get_timestamp_period(log, pname)
            log_period.length = end - start

            log_period.freq_gpu = list()
            for entry in log.freq_gpu:
                if entry.time >= start and entry.time <= end:
                    log_period.freq_gpu.append((entry.time - start, entry.value))
            
            log_period.memory_ram = list()
            # just going to add up total if there are multiple pids
            for pid, entries in log.memory_ram.items():
                for entry in entries:
                    if entry.time >= start and entry.time <= end:
                        p_t = entry.time - start
                        flag = False
                        for prev_ram in log_period.memory_ram:
                            if not flag and prev_ram[0] == p_t:
                                flag = True
                                prev_ram[1] += entry.value
                        if not flag:
                            log_period.memory_ram.append((p_t, entry.value))
            
            log_period.memory_gpu = list()
            # just going to add up total if there are multiple pids
            for pid, entries in log.memory_gpu.items():
                for entry in entries:
                    if entry.time >= start and entry.time <= end:
                        p_t = entry.time - start
                        flag = False
                        for prev_gpu in log_period.memory_gpu:
                            if not flag and prev_gpu[0] == p_t:
                                flag = True
                                prev_gpu[1] += entry.value
                        if not flag:
                            log_period.memory_gpu.append((p_t, entry.value))

            log_period.power = list()
            for entry in log.power:
                if entry.time >= start and entry.time <= end:
                    log_period.power.append((entry.time - start, entry.value))
            
            period_list.append(log_period)
        
        # save periods to the proper TaggedData
        flag_used_old = False
        for prev_tdata in tagged_data_list:
            if not flag_used_old and prev_tdata.has_tags(name):
                # use the old TaggedData
                flag_used_old = True
                prev_tdata._periods.append(period_list)
        if not flag_used_old:
            # make a new TaggedData
            tdata = TaggedData()
            tdata._tags = name
            tdata._periods = list()
            tdata._periods.append(period_list)
            tagged_data_list.append(tdata)

    # move everything into an instance of TaggedDataList and return
    ret = TaggedDataList()
    ret._list = tagged_data_list
    return ret