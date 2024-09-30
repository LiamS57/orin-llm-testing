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


device = "orin-nano-8gb"
max_pm = log_loader.device_pm_dict[device][0]
frame_data: dict[str, dict[str, float]] = dict()
for tagged in data.with_tags(max_pm, device):
    print(tagged._tags)
    lat_load = median([tagged.period('MODEL_LOAD', i).length for i in range(5)])
    lat_gen = median([tagged.period('GENERATE', i).length for i in range(5)])
    lat_total = lat_load + lat_gen
    
    model_name = tagged._tags[0]
    frame_data[model_name] = frame_data.get(model_name, dict())
    if tagged.has_tags(["no-quant"]):
        frame_data[model_name]["No Quantization"] = lat_total
    else:
        frame_data[model_name]["4-bit Quantization"] = lat_total


for k, v in frame_data.items():
    for h, j in v.items():
        print(f'{k}, {h} -> {j}')

df = pd.DataFrame(frame_data).T.sort_index(key=lambda _: pd.Index(log_loader.model_order))
print(df)


fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax)
ax.set_xticklabels(log_loader.model_order, rotation=10)
ax.set_title(f'Total Run Time with/without Quantization per\nModel ({device} at {max_pm})')
ax.set_ylabel('Time (seconds)')
plt.tight_layout()
plt.show()