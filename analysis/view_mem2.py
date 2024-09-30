import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.patches import Patch
import numpy as np
import os
import json

in_folder = os.path.abspath('data-usb')

# important test naming info
def m_name(param):
    return f'pythia-{param}-deduped'
device_order = ['agx-orin-devkit', 'agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', '50W', 'MAXN']
model_params = ['70m', '160m', '410m', '1b', '1.4b']
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






d_gpu = dict()
d_ram = dict()
for dev in device_order:
    d_gpu[dev] = dict()
    d_ram[dev] = dict()
    pm = device_pm_dict[dev][0]
    with_dev_pm = [x for x in existing if dev in x and pm in x]

    for m in model_params:
        llm = m_name(m)

        iters = [x for x in with_dev_pm if llm in x]

        gpu_peaks = list()
        ram_peaks = list()
        for log in [load_log(x[-1]) for x in iters if 'no-quant' not in x]:
            t_load_start, t_load_end = get_times_between_stamps(log, 'MODEL_LOAD')
            t_gen_start, t_gen_end = get_times_between_stamps(log, 'GENERATE')
            def is_within_times(t, t1s, t1e, t2s, t2e):
                return (t1s <= t <= t1e) or (t2s <= t <= t2e)

            series_gpu = log['memory_gpu']
            pid_gpu = list(series_gpu.keys())[0]
            series_ram = log['memory_ram']
            pid_ram = list(series_gpu.keys())[0]
            assert len(series_gpu) == 1
            assert len(series_ram) == 1
            assert pid_gpu == pid_ram

            i_gpu = [x['value'] for x in series_gpu[pid_gpu] if is_within_times(x['time'], t_load_start, t_load_end, t_gen_start, t_gen_end)] # gpu memory for this iteration
            i_ram = [x['value'] for x in series_ram[pid_ram] if is_within_times(x['time'], t_load_start, t_load_end, t_gen_start, t_gen_end)] # cpu memory for this iteration
            i_pk_gpu = np.max(i_gpu) / 1024.0 # peak gpu memory for this iteration
            i_pk_ram = np.max(i_ram) / 1024.0 # peak cpu memory for this iteration

            gpu_peaks.append(i_pk_gpu)
            ram_peaks.append(i_pk_ram)
        gpu_peak = np.median(gpu_peaks)
        ram_peak = np.median(ram_peaks)
        d_gpu[dev][llm] = gpu_peak
        d_ram[dev][llm] = ram_peak

df_gpu = pd.DataFrame(d_gpu)
df_ram = pd.DataFrame(d_ram)
print(df_gpu)
print(df_ram)
print(df_gpu.T['pythia-70m-deduped'])
# exit()

# fig, ax = plt.subplots()
# df.plot(kind='line', ax=ax, style='o-', colormap='autumn')

# ax.set_xticks([0, 1, 2, 3, 4])
# # ax.set_xbound(lower=-0.2, upper=4.2)
# # ax.set_ybound(lower=0)
# # ax.set_xticklabels(model_order, rotation=13, fontsize=12)
# # ax.set_title(f'Quantization Comparison for Generation Latency\n({dev} at {pm}, median run)', fontsize=12)
# # ax.set_ylabel('Latency (s)')
# ax.set_xlabel('Pythia Model')
# # ax.legend(['No Quantization', '4-bit Quantization'])
# # plt.tight_layout()qqq
# # print(f'Quantization Comparison for Generation Latency\n({dev} at {pm}, median run)')
# plt.show()


bspace = 8

cmap = cm.viridis
pos_map = lambda y: np.mod(y, bspace) / len(model_order)


for idev in range(len(device_order)):
    dev = device_order[idev]
    xi = np.array([(j*bspace)+idev for j in range(len(model_order))])
    ci = cmap(pos_map(xi))

    gpubar = plt.bar(x=xi, height=df_gpu[dev], color=ci, width=1)
    rambar = plt.bar(x=xi, height=df_ram[dev], bottom=df_gpu[dev], color=ci, width=1)
    for b in rambar:
        b.set_hatch('xxx')

tmpx = list(range(len(device_order)))
tmp = plt.bar(x=tmpx, height=[1]*len(device_order), color=cmap(pos_map(tmpx)))
leg_dev = plt.legend(handles=tmp, labels=device_order, loc='upper left')

tmp2 = [Patch(edgecolor='black', fill=False, label='RAM'), 
        Patch(edgecolor='black', fill=False, label='VRAM')]
tmp2[0].set_hatch('xxx')
plt.legend(handles=tmp2, loc='center left')

plt.gca().add_artist(leg_dev)
tmp.remove()

plt.xticks([(j*bspace)+2.5 for j in range(len(model_order))])
plt.gca().set_xticklabels(model_params)
plt.xlabel('Pythia Model')
plt.ylabel('Allocated Memory (MB)')
plt.show()