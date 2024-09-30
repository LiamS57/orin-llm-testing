# TODO: gpu mem comparison

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from statistics import median
import os
import log_loader

in_folder = os.path.abspath('data-usb')
data = log_loader.load_logs_from_folder(in_folder)

runs_cols = [(0.8 - n * 0.15, 0.2, 0.2) for n in range(5)]

# pick llm, vary device at max power model (all runs)

print('Varying device')

llm = log_loader.m_name('410m')

d = dict()
for dev in log_loader.device_order:
    d[dev] = list()
for tagged in data.with_and_without_tags([llm], ['no-quant']):
    if tagged._tags[-1] == log_loader.device_pm_dict[tagged._tags[1]][0]:
        print(tagged._tags)
        dev = tagged._tags[1]
        for i in range(5):
            gpu = tagged.period('MODEL_LOAD', i).memory_gpu
            gpu_max = np.max(gpu.T[1]) / 1024.0
            d[dev].append(gpu_max)
        print(len(d[dev]))

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=runs_cols)
ax.set_xticklabels(log_loader.device_order, rotation=10)
ax.set_title(f'Maximum GPU Memory usage during Model Load per Device\n({llm} at maximum power model, with quantization)')
ax.set_ylabel('GPU Memory (MB)')
ax.legend([f'Run {n+1}' for n in range(5)])
ax.set_ylim(0, 750)
plt.show()

# line graph, pick device, 

runs_cols = [(0.8 - n * 0.15, 0.2, 0.2 + n * 0.15) for n in range(5)]

dev = 'agx-orin-32gb'
pm = log_loader.device_pm_dict[dev][0]

d: dict[str, pd.Series] = dict()
for m in log_loader.model_order:
    d[m] = None
for tagged in data.with_and_without_tags([dev, pm], ['no-quant']):
    print(tagged._tags)
    m = tagged._tags[0]
    period = tagged.period('MODEL_LOAD', 2).memory_gpu
    pdict = dict()
    for p in period:
        pdict[p[0]] = p[1]
    d[m] = pd.Series(pdict)

fig, ax = plt.subplots()
j = 0
for m in log_loader.model_order:
    d[m].plot(kind='line', ax=ax, color=runs_cols[j])
    j += 1
ax.set_title(f'GPU Memory usage during Model Load\n({dev} at maximum power model,\nmedian run, with quantization)')
ax.set_ylabel('GPU Memory (MB)')
ax.set_xlabel('Time (s)')
ax.legend(log_loader.model_order)
plt.show()