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

def df_sort_help(x: pd.Index):
    return pd.Index(log_loader.model_order)

def _integrate(arr: np.ndarray) -> float:
    return np.trapezoid(y=arr.T[1], x=arr.T[0])


model = log_loader.m_name('410m')
frame_data: dict[str, dict[str, float]] = dict()
for tagged in data.with_and_without_tags([model], ['no-quant']):
    device_name = tagged._tags[-2]
    if log_loader.device_pm_dict[device_name][0] == tagged._tags[-1]:
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

df = pd.DataFrame(frame_data).T.sort_index(key=lambda _: pd.Index(log_loader.device_order))
print(df)


fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
ax.set_title(f'Total Run Time per Subsequent Runs of {model}\nat Max Power Model per Device')
ax.set_ylabel('Time (seconds)')
plt.tight_layout()
plt.show()