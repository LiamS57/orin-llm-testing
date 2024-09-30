import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.colors as colors
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



def plot_data(dev, llm):
    pm = device_pm_dict[dev][0]

    with_all = [x for x in existing if (dev in x) and (pm in x) and (llm in x)]
    quant = [load_log(x[-1]) for x in with_all if 'no-quant' not in x]
    noquant = [load_log(x[-1]) for x in with_all if 'no-quant' in x]

    lats_load_q = list()
    lats_gen_q = list()
    lats_load_nq = list()
    lats_gen_nq = list()
    for log in quant:
        t_start, t_end = get_times_between_stamps(log, 'MODEL_LOAD')
        lats_load_q.append(t_end - t_start)
        t_start, t_end = get_times_between_stamps(log, 'GENERATE')
        lats_gen_q.append(t_end - t_start)
    for log in noquant:
        t_start, t_end = get_times_between_stamps(log, 'MODEL_LOAD')
        lats_load_nq.append(t_end - t_start)
        t_start, t_end = get_times_between_stamps(log, 'GENERATE')
        lats_gen_nq.append(t_end - t_start)
    lat_load_q = np.median(lats_load_q)
    lat_gen_q = np.median(lats_gen_q)
    lat_load_nq = np.median(lats_load_nq)
    lat_gen_nq = np.median(lats_gen_nq)

    return lat_load_q, lat_gen_q, lat_load_nq, lat_gen_nq

Xi = list(range(len(device_order)))
Yi = list(range(len(model_order)))
X, Y = np.meshgrid(Xi, Yi)
Z_load_q = np.zeros(X.shape)
Z_gen_q = np.zeros(X.shape)
Z_load_nq = np.zeros(X.shape)
Z_gen_nq = np.zeros(X.shape)
for i in range(X.shape[0]):
    for j in range(X.shape[1]):
        dev = device_order[X[i][j]]
        llm = model_order[Y[i][j]]
        Z_load_q[i][j], Z_gen_q[i][j], Z_load_nq[i][j], Z_gen_nq[i][j] = plot_data(dev, llm)


Zlist = [Z_load_q, Z_gen_q, Z_load_nq, Z_gen_nq]
cmaplist = [cm.coolwarm, cm.RdYlGn_r, cm.coolwarm, cm.RdYlGn_r]
norm1 = colors.Normalize(vmin=0, vmax=20)
norm2 = colors.Normalize(vmin=0, vmax=200)
# norm2 = colors.LogNorm(vmin=1, vmax=200, clip=True)
normlist = [norm1, norm2, norm1, norm2]
textlist = [('Model Loading', 'with 4-bit'), 
            ('Total Token Generation', 'with 4-bit'), 
            ('Model Loading', 'without'),
            ('Total Token Generation', 'without')]
for Z, cmap, norm, text in zip(Zlist, cmaplist, normlist, textlist):
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')
    ax.plot_surface(X,Y,Z, norm=norm, cmap=cmap)

    ax.set_xticks(Xi)
    ax.set_xticklabels(['AGX Orin Devkit', 'AGX Orin 32GB', 'NX 16GB', 'NX 8GB', 'Nano 8GB', 'Nano 4GB'])
    for tick in ax.xaxis.get_majorticklabels():
        tick.set_horizontalalignment('left')
        tick.set_verticalalignment('top')
    # ax.set_xlabel('Device Conf')

    ax.set_yticks(Yi)
    ax.set_yticklabels(['70m', '160m', '410m', '1b', '1.4b'])
    for tick in ax.yaxis.get_majorticklabels():
        # tick.set_horizontalalignment('right')
        tick.set_verticalalignment('top')
    ylbl = ax.set_ylabel('Pythia Model')

    ax.set_zbound(lower=0)
    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel('Time    \n(s)    ', rotation=0)
    
    # ax.set_title(f'Median {text[0]} Latency\n(Maximum NV Power Model, {text[1]} Quantization)')
    ax.view_init(azim=-135, elev=25)
    plt.show()