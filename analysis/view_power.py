import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from statistics import median
import os
import log_loader

in_folder = os.path.abspath('data')
data = log_loader.load_logs_from_folder(in_folder)

dev = 'agx-orin-32gb'
pm = log_loader.device_pm_dict[dev][0]

# TODO: all below, but with quant, and then both of those but during MODEL_LOAD

seqs: list[pd.Series] = list()
lgd = list()
for tagged in data.with_and_without_tags([dev, pm, 'no-quant'], []):
    print(tagged._tags)
    d = dict()
    period = tagged.period('GENERATE', 2).power
    for p in period:
        d[p[0]] = p[1]
    seqs.append(pd.Series(d))
    lgd.append(tagged._tags[0])

fig, ax = plt.subplots()
for i in range(len(seqs)):
    seqs[i].plot(kind='line', ax=ax)
ax.legend(lgd)
ax.set_title(f'Power Usage during Generation\n({dev} at {pm}, median run, no quantization)')
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Power Used (W)')
plt.show()



seqs: list[pd.Series] = list()
lgd = list()
for tagged in data.with_and_without_tags([dev, pm], ['no-quant']):
    print(tagged._tags)
    d = dict()
    period = tagged.period('GENERATE', 2).power
    for p in period:
        d[p[0]] = p[1]
    seqs.append(pd.Series(d))
    lgd.append(tagged._tags[0])

fig, ax = plt.subplots()
for i in range(len(seqs)):
    seqs[i].plot(kind='line', ax=ax)
ax.legend(lgd)
ax.set_title(f'Power Usage during Generation\n({dev} at {pm}, median run, with quantization)')
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('Power Used (W)')
plt.show()