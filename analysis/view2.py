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


pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', 'MAXN']
model_order = ['pythia-70m-deduped', 'pythia-160m-deduped', 'pythia-410m-deduped', 'pythia-1b-deduped', 'pythia-1.4b-deduped']
def df_sort_help(x: pd.Index):
    return pd.Index(model_order)

def _integrate(arr: np.ndarray) -> float:
    return np.trapezoid(y=arr.T[1], x=arr.T[0])


frame_data: dict[str, dict[str, float]] = dict()
for tagged in data.with_tags("MAXN", "orin-nx-16gb"):
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

df = pd.DataFrame(frame_data).T.sort_index(key=lambda _: pd.Index(model_order))
print(df)


fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax)
ax.set_xticklabels(model_order, rotation=10)
ax.set_title('Total Run Time with/without Quantization per\nModel (Orin NX 16GB at MAXN)')
ax.set_ylabel('Time (seconds)')
plt.tight_layout()
plt.show()