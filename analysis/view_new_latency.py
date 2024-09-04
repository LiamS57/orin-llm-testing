import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
import os
import json

in_folder = os.path.abspath('../tests/out')

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




# generate graph

d = dict()
for m in model_order:
    d[m] = dict()

found = [x for x in existing if x[0] == 'orin-nano-8gb' and x[1] == '15W' and ('no-quant' not in x)]
print(f'Extracted {len(found)} log paths based on tags')
for f in found:
    data = None
    with open(f[-1], 'r') as fp:
        data = json.load(fp)
    assert data != None

    idle_times = [x['time'] for x in data['timestamps'] if x['value'].startswith('IDLE_')]
    idle_t = idle_times[1] - idle_times[0]

    load_times = [x['time'] for x in data['timestamps'] if x['value'].startswith('MODEL_LOAD_')]
    load_t = load_times[1] - load_times[0]

    gen_times = [x['time'] for x in data['timestamps'] if x['value'].startswith('GENERATE_')]
    gen_t = gen_times[1] - gen_times[0]

    #print(f'{f[:-1]}:   {idle_t} s, {load_t} s, {gen_t} s')

    d[f[2]][f[3]] = gen_t

df = pd.DataFrame(d)
print(df)

fig, ax = plt.subplots()
df.plot(kind='box', ax=ax)
ax.set_xticklabels(model_order, rotation=10)
ax.set_title(f'Generation Latency per LLM\n(orin-nano-8gb at 15W, with quantization)')
ax.set_ylabel('Time (s)')
#ax.legend([f'Run {n+1}' for n in range(5)])
plt.show()


fig, ax = plt.subplots()
df.plot(kind='line', ax=ax)
#ax.set_xticklabels(model_order, rotation=10)
ax.set_title(f'Generation Latency per LLM\n(orin-nano-8gb at 15W, with quantization)')
ax.set_ylabel('Time (s)')
ax.set_xlabel('Iteration (#)')
#ax.legend([f'Run {n+1}' for n in range(5)])
plt.show()