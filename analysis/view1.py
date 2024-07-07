import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np

import os
import sys

import log_loader

if len(sys.argv) != 2:
    print('Need to supply folder to pull data from!')
    exit(1)

in_folder = os.path.abspath(sys.argv[1])
data = log_loader.load_logs_from_folder(in_folder)

def _series_from_tuple_list(tuple_list: list[tuple]) -> pd.Series:
    dct = dict()
    for k, v in tuple_list:
        dct[k] = v
    return pd.Series(dct)

def plot_tlist(param: list[tuple], style='-'):
    _series_from_tuple_list(param).plot(style=style)


#fig, ax = plt.subplots()
#leg = list()

# latencies = dict()
# for tagged in data.with_tags('pythia-410m-deduped'):
#     print(tagged._tags)
#     b = list()
#     for i in range(5):
#         b.append(tagged.period('MODEL_LOAD', i).length)
#     latencies[tagged._tags[2]] = b

# df = pd.DataFrame(latencies).T
# print(df)
# df.plot(kind='bar')
# plt.show()

#pd.Series(latencies).plot(kind='bar')
#plt.show()


    #plot_tlist(tagged.period('GENERATE', 0).memory_gpu)
    #leg.append('_'.join(tagged._tags) + ' (first)')
    #plot_tlist(tagged.period('GENERATE', 4).memory_gpu, style='--')
    #leg.append('_'.join(tagged._tags) + ' (last)')

#tagged = data.with_tags('pythia-1.4b-deduped', 'MAXN')[0]
#for i in range(5):
#    gen_power = tagged.period('MODEL_LOAD', i).power
#    plot_tlist(gen_power)
#    leg.append(str(i))

#latency_list = list()
#for i in range(5):
#    latency_list.append(tagged.period('MODEL_LOAD', i).length)
    #leg.append(str(i))
#pd.Series(latency_list).plot(kind='bar')

#ax.legend(leg)
#plt.show()
    


    # for i in range(len(tagged._periods)):
    #     for per in tagged._periods[i]:
    #         print(f'  ({per.i}) {per.name} -> {per.length:.4f} s')
    #         lines = list()
    #         for t, freq in per.freq_gpu:
    #             lines.append((t, f'{freq} MHz'))
    #         for t, mem in per.memory_ram:
    #             lines.append((t, f'{mem} KB RAM'))
    #         for t, mem in per.memory_gpu:
    #             lines.append((t, f'{mem} KB GPU'))
    #         for t, power in per.power:
    #             lines.append((t, f'{power} W'))
    #         for t, l in sorted(lines, key=lambda x: x[0]):
    #             print(f'    ({t:.4f}): {l}')

model_order = ['pythia-70m-deduped', 'pythia-160m-deduped', 'pythia-410m-deduped', 'pythia-1b-deduped', 'pythia-1.4b-deduped']
def df_sort_help(x: pd.Index):
    return pd.Index(model_order)

def integrate(arr: np.ndarray) -> float:
    return np.trapezoid(y=arr.T[1], x=arr.T[0])

energy_per_model = dict()
for tagged in data.with_tags('MAXN'):
    print(tagged._tags)
    energy_iter = list()
    for i in range(5):
        pwr_idle = tagged.period('IDLE', i).power
        pwr_gen = tagged.period('MODEL_LOAD', i).power
        _, pwr_idle_avg = np.median(pwr_idle, axis=0)

        for entry in pwr_gen:
            entry[1] = entry[1] - pwr_idle_avg
        energy_gen = integrate(pwr_gen)
        #pwr_gen_true_avg = energy_gen / tagged.period('GENERATE', i).length
        print(f' ({i}): {energy_gen} J')
        energy_iter.append(energy_gen)
    energy_per_model[tagged._tags[0]] = energy_iter

fig, ax = plt.subplots()

df = pd.DataFrame(energy_per_model).T.sort_index(key=lambda _: pd.Index(model_order))
#df = pd.DataFrame(energy_per_model).T
print(df)
df.plot(kind='bar', ax=ax)

ax.set_xticklabels(model_order, rotation=10)
ax.set_title('Energy Used per Model')
ax.set_ylabel('Energy Used (Joules)')
ax.legend(['Run 1', 'Run 2', 'Run 3', 'Run 4', 'Run 5'])
plt.tight_layout()
plt.show()