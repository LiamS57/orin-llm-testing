import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import os
import json

in_folder = os.path.abspath('data-usb')

# important test naming info
def m_name(param):
    return f'pythia-{param}-deduped'
device_order = ['agx-orin-devkit', 'agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', '50W', 'MAXN']
model_order = [m_name('70m'), m_name('160m'), m_name('410m'), m_name('1b'), m_name('1.4b')]
device_pm_dict = {
    'agx-orin-devkit': ['MAXN', '50W', '30W', '15W'],
    'agx-orin-32gb': ['MAXN', '40W', '30W', '15W'],
    'orin-nx-16gb': ['MAXN', '25W', '15W', '10W'],
    'orin-nx-8gb': ['MAXN', '20W', '15W', '10W'],
    'orin-nano-8gb': ['15W', '7W'],
    'orin-nano-4gb': ['10W', '7W-AI', '7W-CPU']
}


def get_times_between_stamps(data: dict, prefix: str) -> tuple[float, float]:
    start = -1
    end = -1
    for entry in data['timestamps']:
        t = entry['time']
        v = entry['value']
        if prefix in v:
            if 'START' in v:
                start = t
            elif 'END' in v:
                end = t
    assert start >= 0
    assert end >= 0
    return start, end

def load_log(path: str) -> dict:
    with open(path, 'r') as fp:
        return json.load(fp)
    
def integrate(lst: list[tuple]) -> float:
    acc = 0
    for j in range(len(lst) - 1):
        t0 = lst[j][0]
        v0 = lst[j][1]
        t1 = lst[j+1][0]
        v1 = lst[j+1][1]
        t_delta = t1 - t0
        v_avg = (v0 + v1) / 2
        acc += (v_avg * t_delta)
    return acc


# get all logs
print('Searching...')

log_paths = list()
for p, _, fs in list(os.walk(in_folder)):
    for f in fs:
        if f.startswith('log_') and f.endswith('json'):
            log_paths.append(os.path.join(p, f))

print(f'Found {len(log_paths)} logs\nLoading details...')

# begin
existing = list()
max_iterations = 0

for path in log_paths:
    data = os.path.basename(path)[4:-5].split('_')
    tags = list()
    tags.append(data.pop(-2)) # device
    tags.append(data.pop(-1)) # pm
    tags.append(data.pop(0)) # model
    iters = int(data.pop(0))
    max_iterations = max(max_iterations, iters)
    tags.append(iters) # iteration
    if len(data) > 0:
        tags = tags + data
    tags.append(path) # add to the end
    
    existing.append(tags)

existing.sort()


d = dict()
dev = device_order[2]
pm = device_pm_dict[dev][0]

with_dev_pm = [x for x in existing if dev in x and pm in x]

for m in model_order:
    d[m] = dict()

    with_m = [x for x in with_dev_pm if m in x]

    latencies = list()
    for log in [load_log(x[-1]) for x in with_m if 'no-quant' not in x]:
        t_start, t_end = get_times_between_stamps(log, 'GENERATE')
        latencies.append(t_end - t_start)
    d[m]['q'] = np.median(latencies) # median value in iterations

    latencies = list()
    for log in [load_log(x[-1]) for x in with_m if 'no-quant' in x]:
        t_start, t_end = get_times_between_stamps(log, 'GENERATE')
        latencies.append(t_end - t_start)
    d[m]['nq'] = np.median(latencies) # median value in iterations

df = pd.DataFrame(d).T
print(df)



runs_cols = [(0.85, 0.15, 0.15), (0.15, 0.15, 0.85)]
fig, ax = plt.subplots()
df.plot(kind='barh', ax=ax, color=runs_cols)
# ax.set_xticklabels(model_order, rotation=13, fontsize=12)
ax.set_title(f'Quantization Comparison for Generation Latency\n({dev} at {pm}, median run)', fontsize=12)
ax.set_xlabel('Latency (s)', fontsize=12)
ax.legend(['4-bit Quantization', 'No Quantization'])
plt.tight_layout()
plt.show()





#     for pm in device_pm_dict[dev]:
#         with_pm = [x for x in with_dev if pm in x]
#         #with_pm_q = [x for x in with_pm if 'no-quant' not in x]
#         #with_pm_nq = [x for x in with_pm if 'no-quant' in x]
#         # print(f'{dev} {pm} -> {len(with_pm_q)}')
#         with_pm.sort(key=lambda x: (len(x), model_order.index(x[2]), x[3]))
#         # max_i = 0
#         # for j in range(len(with_pm)):
#         #     if 'no-quant' not in with_pm[j]:
#         #         with_pm[j].insert(4, 'quant')
#         #     max_i = max(with_pm[j][3], max_i)

        
#         info = dict()
#         info['quant'] = dict()
#         info['no-quant'] = dict()
#         for llm in model_order:
#             info['quant'][llm] = list()
#             info['no-quant'][llm] = list()

#         for tags in with_pm:
#             path = tags[-1]
#             with open(path, 'r') as fp:
#                 data = json.load(fp)
#                 lat = get_latency_between_stamps(data, 'MODEL_LOAD')
#                 if 'no-quant' in tags:
#                     info['no-quant'][tags[2]].append(lat)
#                 else:
#                     info['quant'][tags[2]].append(lat)

        
#         print(f'& {pm}', end='')
#         for q in ['quant', 'no-quant']:
#             for llm in model_order:
#                 median = -1
#                 if len(info[q][llm]) > 0:
#                     median = np.median(info[q][llm])
#                 print(f' & {median:.3f}', end='')

#         print(' \\\\')