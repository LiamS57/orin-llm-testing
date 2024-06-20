# Helper functions for logging statistics.
# 
# Although it is possible to set up multiple Log class instances, it is recommended to use
# the begin_log() and end_log() functions instead. Multiple instances of jtop with different
# intervals do not function at the proper intervals together, so it is better to only run
# one at a time.
# 
# jtop reference: https://rnext.it/jetson_stats/reference/jtop.html 
# 
# Liam Seymour 6/18/24

from json import dumps, loads, JSONDecoder, JSONEncoder
from jtop import jtop
from time import perf_counter, sleep
from typing import Any
from typing_extensions import Self

def get_time() -> float:
    # wrapper for perf_counter, in case we need to use something else or add functionality later
    return perf_counter()

class LogEntry:
    '''Simple "struct" for storing a value along with the time it is added to the log.'''
    time: float
    value: Any

    def __init__(self, time: float, value):
        self.time = time
        self.value = value

class Log:
    '''Contains logged data from a logging session.'''

    time_log_start: float
    '''Beginning time of the log (in seconds).'''
    time_log_end: float
    '''Ending time of the log (in seconds).'''
    timestamps: list[LogEntry]
    '''List of timestamp entries in the log.
    Useful for storing information on events that take place during logging.'''
    memory_ram: dict[int, list[LogEntry]]
    '''Dictionary of lists of RAM measurements (in KB). 
    The dictionary is indexed by the PID of the pt_main_thread process(es) seen by jtop.
    Lists in the dictionary store measurements along with the time they are recorded since the log began (in seconds).'''
    memory_gpu: dict[int, list[LogEntry]]
    '''Dictionary of lists of GPU memory measurements (in KB). 
    The dictionary is indexed by the PID of the pt_main_thread process(es) seen by jtop.
    Lists in the dictionary store measurements along with the time they are recorded since the log began (in seconds).'''
    power: list[LogEntry]
    '''List of power measurements (in watts), along with the time they are recorded since the log began (in seconds).'''

    _jtop: jtop

    def __init__(self):
        self.time_log_start = -1
        self.time_log_end = -1
        self.timestamps = list()
        self.memory_ram = dict()
        self.memory_gpu = dict()
        self.power = list()
    
    def _t(self) -> float:
        return get_time() - self.time_log_start

    def _log(self, jetson: jtop):
        '''internal logging callback function for jtop'''
        # get time since the log began
        t = self._t()

        # log power data
        self.power.append(LogEntry(t, (jetson.power['tot']['power'] / 1000)))

        # log process-specific data
        for proc in jetson.processes:
            # pytorch process we want is always called 'pt_main_thread', GPU mem usage reflects model loading
            if proc[9] == "pt_main_thread":
                pid = proc[0]
                if not pid in self.memory_ram:
                    self.memory_ram[pid] = list()
                if not pid in self.memory_gpu:
                    self.memory_gpu[pid] = list()
                
                # log RAM and GPU memory
                self.memory_ram[pid].append(LogEntry(t, proc[7]))
                self.memory_gpu[pid].append(LogEntry(t, proc[8]))
    
    def _log_timestamp(self, info):
        self.timestamps.append(LogEntry(self._t(), info))

    class _LogJSONEncoder(JSONEncoder):
        def default(self, o: Any) -> Any:
            if isinstance(o, (Log, LogEntry)):
                return o.__dict__
            else:
                return super().default(o)
    
    class _LogJSONDecoder(JSONDecoder):
        def __init__(self, **kwargs):
            kwargs.setdefault("object_hook", self.object_hook)
            super().__init__(**kwargs)
        
        def object_hook(self, o):
            if isinstance(o, dict):
                if len(o.items()) == 2 and 'time' in o and 'value' in o:
                    return LogEntry(o['time'], o['value'])
            return o
    
    def to_json(self) -> str:
        '''Converts Log object to json string.'''
        return dumps(self, cls=Log._LogJSONEncoder, indent=4)

    def from_json(json_str: str) -> Self:
        '''Converts json string to Log object.'''
        newlog = Log()
        newlog.__dict__ = loads(json_str, cls=Log._LogJSONDecoder)
        return newlog
    
    def print(self, in_order: bool = False):
        '''Prints log data in the console.
        Can either be printed with all entries grouped by content, or in order based on time.'''
        total_t = self.time_log_end - self.time_log_start
        print(f'Start time: {self.time_log_start:.4f} s (t=0)')
        print(f'End time: {self.time_log_end:.4f} s (t={total_t:.4f})')
        if in_order:
            # Print all entries in order based on time added

            entries: list[tuple[float, str]] = list()

            # timestamps
            for entry in self.timestamps:
                val_str = '<--- ' + entry.value
                entries.append((entry.time, val_str))

            # power
            for entry in self.power:
                val_str = f'Power: {entry.value} W'
                entries.append((entry.time, val_str))

            # ram
            for pid, mem_list in self.memory_ram.items():
                for entry in mem_list:
                    val_str = f'RAM (PID: {pid}): {int(entry.value / 1000)} MB'
                    entries.append((entry.time, val_str))

            # gpu memory
            for pid, mem_list in self.memory_gpu.items():
                for entry in mem_list:
                    val_str = f'GPU MEM (PID: {pid}): {int(entry.value / 1000)} MB'
                    entries.append((entry.time, val_str))
            
            # print entries in order
            for entry in sorted(entries, key=lambda e : e[0]):
                print(f'({entry[0]:.4f} s): {entry[1]}')
            
        else:
            # Print all entries grouped by content

            print('Timestamps:')
            for entry in self.timestamps:
                print(f'  ({entry.time:.4f} s): {entry.value}')

            print('Power Usage:')
            for entry in self.power:
                print(f'  ({entry.time:.4f} s): {entry.value} W')

            print('RAM Usage:')
            for pid, mem_list in self.memory_ram.items():
                print(f'  PID: {pid}')
                for entry in mem_list:
                    print(f'    ({entry.time:.4f} s): {int(entry.value / 1000)} MB')

            print('GPU Mem Usage:')
            for pid, mem_list in self.memory_gpu.items():
                print(f'  PID: {pid}')
                for entry in mem_list:
                    print(f'    ({entry.time:.4f} s): {int(entry.value / 1000)} MB')



_running_log: (Log | None) = None

def begin_log(interval=0.5):
    '''Begin a statistics log. Raises a RuntimeError if a log is already running.'''
    global _running_log
    if _running_log != None:
        raise RuntimeError('Attempted to start a log measurement when already logging!')
    
    _running_log = Log()
    _running_log._jtop = jtop(interval=interval)
    _running_log._jtop.attach(_running_log._log)
    _running_log.time_log_start = get_time()
    _running_log._log_timestamp('Log started')
    _running_log._jtop.start()

def end_log() -> Log:
    '''Finish a running log and return the data. Raises a RuntimeError if begin_log() is not run first.'''
    global _running_log
    if _running_log == None:
        raise RuntimeError('Attempted to return a log when the log hasn\'t started logging!')
    
    _running_log._jtop.close()
    _running_log._log_timestamp('Log finished')
    _running_log.time_log_end = get_time()
    del _running_log._jtop

    ret = _running_log
    _running_log = None
    return ret

def run_blocking(duration: float, interval=0.5) -> Log:
    '''Log for a set duration, blocking the thread until completed.
    Useful for taking a baseline measurement when not running a test.'''
    begin_log(interval)
    sleep(duration)
    return end_log()

def add_log_timestamp(info: str):
    '''Adds a timestamp string to a running log. Raises a RuntimeError if begin_log() is not run first.'''
    global _running_log
    if _running_log == None:
        raise RuntimeError('Attempted to add a log timestamp when the log hasn\'t started logging!')
    
    _running_log._log_timestamp(info)