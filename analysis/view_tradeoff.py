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
    mi = m.split('-')[1]
    d[mi] = dict()

    with_m = [x for x in with_dev_pm if m in x]

    latencies = list()
    for log in [load_log(x[-1]) for x in with_m if 'no-quant' in x]:
        t_start, t_end = get_times_between_stamps(log, 'GENERATE')
        latencies.append(t_end - t_start)
    d[mi]['nq'] = np.median(latencies)

    latencies = list()
    for log in [load_log(x[-1]) for x in with_m if 'no-quant' not in x]:
        t_start, t_end = get_times_between_stamps(log, 'GENERATE')
        latencies.append(t_end - t_start)
    d[mi]['q'] = np.median(latencies)

df = pd.DataFrame(d).T
print(df)



runs_cols = [(0.85, 0.15, 0.15), (0.15, 0.15, 0.85)]
fig, ax = plt.subplots()
df.plot(kind='line', ax=ax, style='o-', colormap='bwr')

ax.set_xticks([0, 1, 2, 3, 4])
ax.set_xbound(lower=-0.2, upper=4.2)
ax.set_ybound(lower=0)
# ax.set_xticklabels(model_order, rotation=13, fontsize=12)
# ax.set_title(f'Quantization Comparison for Generation Latency\n({dev} at {pm}, median run)', fontsize=12)
ax.set_ylabel('Latency (s)')
ax.set_xlabel('Pythia Model')
ax.legend(['No Quantization', '4-bit Quantization'])
# plt.tight_layout()qqq
print(f'Quantization Comparison for Generation Latency\n({dev} at {pm}, median run)')
plt.show()