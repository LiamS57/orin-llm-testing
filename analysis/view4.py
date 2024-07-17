import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from statistics import median

import os
import sys

import log_loader

if len(sys.argv) != 2:
    print('Need to supply folder to pull data from!')
    exit(1)

in_folder = os.path.abspath(sys.argv[1])
data = log_loader.load_logs_from_folder(in_folder)

device_dict = {
    'agx-orin-32gb': ['MAXN', '40W', '30W', '15W'],
    'orin-nx-16gb': ['MAXN', '25W', '15W', '10W'],
    'orin-nx-8gb': ['MAXN', '20W', '15W', '10W'],
    'orin-nano-8gb': ['15W', '7W'],
    'orin-nano-4gb': ['10W', '7W-AI', '7W-CPU']
}
device_order = ['agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', 'MAXN']
def m_name(param):
    return f'pythia-{param}-deduped'
model_order = [m_name('70m'), m_name('160m'), m_name('410m'), m_name('1b'), m_name('1.4b')]


seqs = list()
for tagged in data.with_and_without_tags([m_name('1.4b'), 'agx-orin-32gb', device_dict['agx-orin-32gb'][0]], ['no-quant']):
    print(tagged._tags)
    for i in range(5):
        d = dict()
        period = tagged.period('MODEL_LOAD', i).memory_gpu
        for p in period:
            d[p[0]] = p[1] / 1024.0
        seqs.append(pd.Series(d))

"""
for k, v in frame_data.items():
    for h, j in v.items():
        print(f'{k}, {h} -> {j}')

df = pd.DataFrame(frame_data).T.sort_index(key=lambda _: pd.Index(device_order))
print(df)"""


fig, ax = plt.subplots()
for i in range(len(seqs)):
    seqs[i].plot(kind='line', ax=ax)
ax.legend([f'Run {x+1}' for x in range(5)])
ax.set_title(f'GPU Memory usage by Subsequent Loads of\n{m_name('1.4b')} (AGX Orin 32GB at MAXN)')
ax.set_xlabel('Time (seconds)')
ax.set_ylabel('GPU Memory Used (MB)')
plt.tight_layout()
plt.show()