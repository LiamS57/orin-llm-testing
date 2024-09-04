# TODO: general time comparison

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from statistics import median
import os
import log_loader

in_folder = os.path.abspath('data')
data = log_loader.load_logs_from_folder(in_folder)

runs_cols = [(0.8 - (n/4)*0.6, 0.2, (n/4)*0.6 + 0.2) for n in range(5)]

# pick device, pick power model, vary llm (show all runs)

print('Varying LLM')
dev = 'agx-orin-32gb'
pm = log_loader.device_pm_dict[dev][0]

d = dict()
for m in log_loader.model_order:
    d[m] = None
for tagged in data.with_and_without_tags([dev, pm], ['no-quant']):
    print(tagged._tags)
    runs = list()
    for i in range(5):
        #load_time = tagged.period('MODEL_LOAD', i).length
        gen_time = tagged.period('GENERATE', i).length
        #runs.append(load_time + gen_time)
        runs.append(gen_time)
    d[tagged._tags[0]] = runs

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=runs_cols)
ax.set_xticklabels(log_loader.model_order, rotation=10)
ax.set_title(f'Generation Latency per LLM\n({dev} at {pm}, with quantization)')
ax.set_ylabel('Time (s)')
ax.legend([f'Run {n+1}' for n in range(5)])
plt.show()


# pick device, vary power model, vary llm (3rd run)

print('Varying LLM and PM')
dev = 'agx-orin-32gb'

d = dict()
for m in log_loader.model_order:
    d[m] = dict()
    for pm in log_loader.device_pm_dict[dev]:
        d[m][pm] = None
for tagged in data.with_and_without_tags([dev], ['no-quant']):
    print(tagged._tags)
    pm = tagged._tags[-1]
    m = tagged._tags[0]
    gen_time = tagged.period('GENERATE', 2).length
    d[m][pm] = gen_time

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=runs_cols)
ax.set_xticklabels(log_loader.model_order, rotation=10)
ax.set_title(f'Generation Latency per LLM at different Power Models\n({dev}, median run, with quantization)')
ax.set_ylabel('Time (s)')
plt.show()


# pick device, pick llm, vary power model (show all runs)

print('Varying PM')
dev = 'agx-orin-32gb'
llm = log_loader.m_name('410m')

d = dict()
for pm in log_loader.device_pm_dict[dev]:
    d[pm] = list()
for tagged in data.with_and_without_tags([dev, llm], ['no-quant']):
    print(tagged._tags)
    pm = tagged._tags[-1]
    for i in range(5):
        gen_time = tagged.period('GENERATE', i).length
        d[pm].append(gen_time)

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=runs_cols)
ax.set_xticklabels(log_loader.device_pm_dict[dev], rotation=0)
ax.set_title(f'Generation Latency per Power Model\n({llm} on {dev}, with quantization)')
ax.set_ylabel('Time (s)')
ax.legend([f'Run {n+1}' for n in range(5)])
plt.show()


# pick llm, vary device, use max power model

print('Varying Device')
llm = log_loader.m_name('160m')

d = dict()
for dev in log_loader.device_order:
    d[dev] = list()
for tagged in data.with_and_without_tags([llm], ['no-quant']):
    if tagged._tags[-1] == log_loader.device_pm_dict[tagged._tags[1]][0]:
        print(tagged._tags)
        dev = tagged._tags[1]
        for i in range(5):
            gen_time = tagged.period('GENERATE', i).length
            d[dev].append(gen_time)

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=runs_cols)
ax.set_xticklabels(log_loader.device_order, rotation=10)
ax.set_title(f'Generation Latency per Device\n({llm} at maximum power model, with quantization)')
ax.set_ylabel('Time (s)')
ax.legend([f'Run {n+1}' for n in range(5)])
plt.show()


# pick device, pick power model, vary llm (compare quant/no-quant)

print('Varying LLM with Quantization')
dev = 'orin-nx-16gb'
pm = log_loader.device_pm_dict[dev][0]

d = dict()
for m in log_loader.model_order:
    d[m] = dict()
    d[m]['quant'] = 0
    d[m]['no-quant'] = 0
for tagged in data.with_tags(dev, pm):
    print(tagged._tags)
    m = tagged._tags[0]
    gen_time = tagged.period('GENERATE', 2).length
    if tagged.has_tags(['no-quant']):
        d[m]['no-quant'] = gen_time
    else:
        d[m]['quant'] = gen_time

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=[(0.8, 0.2, 0.2), (0.2, 0.2, 0.8)])
ax.set_xticklabels(log_loader.model_order, rotation=10)
ax.set_title(f'Generation Latency Quantization Comparison\n({dev} at {pm}, median run)')
ax.set_ylabel('Time (s)')
ax.legend(['4-bit Quantization', 'No Quantization'])
plt.show()