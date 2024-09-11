# TODO: estimated energy usage total, estimated energy per token

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

# get all logs
print('Searching...')

log_paths = list()
for p, _, fs in list(os.walk(in_folder)):
    for f in fs:
        if f.startswith('log_') and f.endswith('json'):
            log_paths.append(os.path.join(p, f))

print(f'Found {len(log_paths)} logs\nLoading details...')

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




runs_cols = [(0.2, 0.8 - n * 0.2, 0.2) for n in range(5)]

# def _integrate(arr: np.ndarray) -> float:
#     return np.trapezoid(y=arr.T[1], x=arr.T[0])

def integrate(lst: list[tuple]):
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

def get_series(data, series_name, stamp_name):
    t_start, t_end = get_times_between_stamps(data, stamp_name)
    series = [(x['time'], x['value']) for x in data[series_name] if x['time'] >= t_start and x['time'] <= t_end]
    return series

# pick device, vary llm and power model

for dev in device_order:

    # dev = 'orin-nx-16gb'
    print(f'Energy for {dev}')

    data = dict()
    d = dict()
    for m in model_order:
        data[m] = dict()
        d[m] = dict()
        for pm in device_pm_dict[dev]:
            iters = [x for x in existing if dev in x and m in x and pm in x and 'no-quant' not in x]
            data[m][pm] = list()
            for x in iters:
                with open(x[-1], 'r') as fp:
                    data[m][pm].append(json.load(fp))
            d[m][pm] = 0

    for llm, data2 in data.items():
        for pm, data3 in data2.items():
            # max_powers = list()
            energies = list()
            for j in range(len(data3)):
                idle_power_srs = get_series(data3[j], 'power', 'IDLE')
                gen_power_srs = get_series(data3[j], 'power', 'GENERATE')

                idle_power_v = [x[1] for x in idle_power_srs]
                median_idle_power = np.median(idle_power_v)

                gen_power_delta_srs = [(x[0], x[1] - median_idle_power) for x in gen_power_srs]

                # for j in range(len(gen_power_srs)):
                #     print(f'{gen_power_srs[j]} - {median_idle_power} -> {gen_power_delta_srs[j]}')
                # exit()
                
                # print(f'{t_end - t_start} s, ~{np.mean(gen_power_v)} W -> estimate: {np.mean(gen_power_v) * (t_end - t_start)} W')
                energy = integrate(gen_power_delta_srs)
                energies.append(energy)
            med = np.median(energies)
            # print(f'{dev} {pm} {llm} -> {med} J')
            # exit()
            d[llm][pm] = med

    df = pd.DataFrame(d).T
    print(df)

    fig, ax = plt.subplots()
    df.plot(kind='bar', ax=ax, color=runs_cols)
    ax.set_xticklabels(model_order, rotation=10)
    ax.set_title(f'Estimated Energy usage during Generation\n({dev} with quantization)')
    ax.set_ylabel('Energy (J)')
    plt.show()