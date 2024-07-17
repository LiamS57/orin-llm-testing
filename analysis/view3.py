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
model_order = ['pythia-70m-deduped', 'pythia-160m-deduped', 'pythia-410m-deduped', 'pythia-1b-deduped', 'pythia-1.4b-deduped']
def df_sort_help(x: pd.Index):
    return pd.Index(model_order)

def _integrate(arr: np.ndarray) -> float:
    return np.trapezoid(y=arr.T[1], x=arr.T[0])

def m_name(param):
    return f'pythia-{param}-deduped'

frame_data: dict[str, dict[str, float]] = dict()
for tagged in data.with_and_without_tags([m_name('410m')], ['no-quant']):
    device_name = tagged._tags[-2]
    if device_dict[device_name][0] == tagged._tags[-1]:
        print(tagged._tags)
        frame_data[device_name] = frame_data.get(device_name, dict())
        for i in range(5):
            lat_load = tagged.period('MODEL_LOAD', i).length
            lat_gen = tagged.period('GENERATE', i).length
            lat_total = lat_load + lat_gen

            frame_data[device_name][f'Run {i + 1}'] = lat_total


for k, v in frame_data.items():
    for h, j in v.items():
        print(f'{k}, {h} -> {j}')

df = pd.DataFrame(frame_data).T.sort_index(key=lambda _: pd.Index(device_order))
print(df)


fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.set_title(f'Total Run Time per Subsequent Runs of {m_name('410m')}\nat Max Power Model per Device')
ax.set_ylabel('Time (seconds)')
plt.tight_layout()
plt.show()