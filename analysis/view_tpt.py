import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Patch
import numpy as np
import os
import json

in_folder = os.path.abspath('../tests/out')

# important test naming info
def m_name(param):
    return f'pythia-{param}-deduped'
device_order = ['agx-orin-devkit', 'agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', '50W', 'MAXN']
model_params = ['70m', '160m', '410m', '1.4b']
model_order = [m_name(x) for x in model_params]
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

for dev in device_order:
    d[dev] = dict()

    with_dev = [x for x in existing if (dev in x) and ('no-quant' not in x)]
    pm = device_pm_dict[dev][0]
    with_pm = [x for x in with_dev if pm in x]

    for m in model_order:
        iters = [x for x in with_pm if m in x]
        iter_logs = [load_log(x[-1]) for x in iters]

        tpts = list()
        for log in iter_logs:
            t_start, t_end = get_times_between_stamps(log, 'GENERATE')
            t_gen = t_end - t_start
            num_tokens = log['tokens_generated']
            tpts.append(t_gen / num_tokens) # append the amount of time taken divided by the number of tokens
        tpt = np.mean(tpts) # average tpt

        d[dev][m] = tpt

df = pd.DataFrame(d)
print(df)


# runs_cols = [(0.85, 0.15, 0.15), (0.55, 0.15, 0.15), (0.15, 0.85, 0.15), (0.15, 0.55, 0.15), (0.15, 0.15, 0.85), (0.15, 0.15, 0.55)]
fig, ax = plt.subplots()
# df.plot(kind='bar', ax=ax, color=runs_cols)

bspace = 9
cmap = lambda idev: cm.Paired(0.49 - (idev / 12.0))
for idev in range(len(device_order)):
    dev = device_order[idev]
    xi = [(j*bspace)+idev for j in range(len(model_order))]
    ax.bar(x=xi, height=df[dev], color=cmap(idev), width=1)

# tmp2 = [Patch(edgecolor='black', fill=False, label='RAM'), 
#         Patch(edgecolor='black', fill=False, label='VRAM')]
leg = [Patch(facecolor=cmap(j), label=device_order[j]) for j in range(len(device_order))]
ax.legend(handles=leg)

ax.set_xticks([(j*bspace)+2.5 for j in range(len(model_order))])
ax.set_xticklabels(model_params, rotation=0)
ax.set_xlabel('Pythia Model')
# ax.set_title(f'Estimated Average Time per Token\n(median run, max power model, with quantization)', fontsize=12)
ax.set_ylabel('Time per Token (s)')
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