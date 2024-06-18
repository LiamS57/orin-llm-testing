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

from jtop import jtop
from time import perf_counter, sleep
from typing import Any

def get_time() -> float:
    # wrapper for perf_counter, in case we need to use something else or add functionality later
    return perf_counter()

class LogEntry:
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
        self.memory_ram = dict()
        self.memory_gpu = dict()
        self.power = list()

    def _log(self, jetson: jtop):
        # get time since the log began
        t = get_time() - self.time_log_start

        # log power data
        self.power.append(LogEntry(t, (jetson.power['tot']['power'] / 1000)))

        # log process-specific data
        for proc in jetson.processes:
            if proc[9] == "pt_main_thread":
                pid = proc[0]
                if not pid in self.memory_ram:
                    self.memory_ram[pid] = list()
                if not pid in self.memory_gpu:
                    self.memory_gpu[pid] = list()
                
                # log RAM and GPU memory
                self.memory_ram[pid].append(LogEntry(t, proc[7]))
                self.memory_gpu[pid].append(LogEntry(t, proc[8]))




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
    _running_log._jtop.start()

def end_log() -> Log:
    '''Finish a running log and return the data. Raises a RuntimeError if begin_log() is not run first.'''
    global _running_log
    if _running_log == None:
        raise RuntimeError('Attempted to return a log when the log hasn\'t started logging!')
    
    _running_log._jtop.close()
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