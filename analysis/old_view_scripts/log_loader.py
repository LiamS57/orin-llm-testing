# Helper script for loading a folder of logs for analysis.

#import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, '../tests')
from statlog import Log

class LogPeriod:
    name: str
    i: int
    length: float
    freq_gpu: np.ndarray
    memory_ram: np.ndarray
    memory_gpu: np.ndarray
    power: np.ndarray
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
    
    def without_tags(self, *tags) -> list[TaggedData]:
        return [tagged for tagged in self._list if not tagged.has_tags(list(tags))]
    
    def with_and_without_tags(self, tags_with: list, tags_without: list) -> list[TaggedData]:
        return [tagged for tagged in self._list if tagged.has_tags(tags_with) and not tagged.has_tags(tags_without)]

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
            except:
                pass
    print(f'Loaded {len(loaded)} files')

    # move loaded data into dict, grouping iterations together
    loaded_iter_groups: dict[str, list[tuple[int, Log]]] = dict()
    for name, log in sorted(loaded, key=lambda x: x[0]):
        i = int(name.pop(1)) # this fragment is an iteration number, the rest are used as tags
        name_str = '_'.join(name)

        if name_str not in loaded_iter_groups:
            loaded_iter_groups[name_str] = list()
        
        loaded_iter_groups[name_str].append((i, log))
        loaded_iter_groups[name_str] = sorted(loaded_iter_groups[name_str], key=lambda x: x[0])
    
    # move grouped data into tagged data
    tagged_data_list: list[TaggedData] = list()
    for name_str, iter_list in loaded_iter_groups.items():
        tagged_data = TaggedData()
        tagged_data._tags = name_str.split('_')
        
        iter_periods_list: list[list[LogPeriod]] = list()
        for i, log in iter_list:
            # get period names in iteration
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

                tmp: list[tuple[float, float]] = list()
                for entry in log.freq_gpu:
                    if entry.time >= start and entry.time <= end:
                        tmp.append((entry.time - start, entry.value))
                log_period.freq_gpu = np.array(tmp)
                
                tmp: list[tuple[float, float]] = list()
                # just going to add up total if there are multiple pids
                for pid, entries in log.memory_ram.items():
                    for entry in entries:
                        if entry.time >= start and entry.time <= end:
                            p_t = entry.time - start
                            flag = False
                            for prev_ram in tmp:
                                if not flag and prev_ram[0] == p_t:
                                    flag = True
                                    prev_ram[1] += entry.value
                            if not flag:
                                tmp.append((p_t, entry.value))
                log_period.memory_ram = np.array(tmp)
                
                tmp: list[tuple[float, float]] = list()
                # just going to add up total if there are multiple pids
                for pid, entries in log.memory_gpu.items():
                    for entry in entries:
                        if entry.time >= start and entry.time <= end:
                            p_t = entry.time - start
                            flag = False
                            for prev_gpu in tmp:
                                if not flag and prev_gpu[0] == p_t:
                                    flag = True
                                    prev_gpu[1] += entry.value
                            if not flag:
                                tmp.append((p_t, entry.value))
                log_period.memory_gpu = np.array(tmp)

                tmp: list[tuple[float, float]] = list()
                for entry in log.power:
                    if entry.time >= start and entry.time <= end:
                        tmp.append((entry.time - start, entry.value))
                log_period.power = np.array(tmp)
                
                period_list.append(log_period)

            iter_periods_list.append(period_list)
        
        # save periods and append tagged data
        tagged_data._periods = sorted(iter_periods_list, key=lambda x: x[0].i)
        tagged_data_list.append(tagged_data)
    

    # move everything into an instance of TaggedDataList and return
    print(f'Processed {len(tagged_data_list)} configurations')
    ret = TaggedDataList()
    ret._list = tagged_data_list
    return ret


def m_name(param):
    return f'pythia-{param}-deduped'

device_order = ['agx-orin-devkit', 'agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', '50W', 'MAXN']
model_order = [m_name('70m'), m_name('160m'), m_name('410m'), m_name('1b'), m_name('1.4b')]
device_pm_dict = {
    'agx-orin-devkit': ['MAXN', '50W', '30W', '15W'],
    'agx-orin-32gb': ['MAXN', '40W', '30W', '15W'],
    'orin-nx-16gb': ['MAXN', '25W', '15W', '10W'],
    'orin-nx-8gb': ['MAXN', '20W', '15W', '10W'],
    'orin-nano-8gb': ['15W', '7W'],
    'orin-nano-4gb': ['10W', '7W-AI', '7W-CPU']
}