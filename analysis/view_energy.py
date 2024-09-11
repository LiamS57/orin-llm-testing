# TODO: estimated energy usage total, estimated energy per token

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
import numpy as np
from statistics import median
import os
import log_loader

in_folder = os.path.abspath('data-usb/week7')
data = log_loader.load_logs_from_folder(in_folder)

runs_cols = [(0.2, 0.8 - n * 0.2, 0.2) for n in range(5)]

def _integrate(arr: np.ndarray) -> float:
    return np.trapezoid(y=arr.T[1], x=arr.T[0])

# pick device, vary llm and power model

print('Energy')

dev = 'orin-nx-16gb'

d = dict()
for m in log_loader.model_order:
    d[m] = dict()
    for pm in log_loader.device_pm_dict[dev]:
        d[m][pm] = 0
for tagged in data.with_and_without_tags([dev], ['no-quant']):
    print(tagged._tags)
    pm = tagged._tags[-1]
    m = tagged._tags[0]

    # power
    idle_power = tagged.period('IDLE', 2).power
    _, idle_power_med = np.median(idle_power, axis=0)
    gen_power = tagged.period('GENERATE', 2).power

    # energy = 0
    # for j in range(1, gen_power.shape[0]):
    #     dt = gen_power[j][0] - gen_power[j-1][0]
    #     pwr = (gen_power[j][1] + gen_power[j-1][1]) / 2
    #     energy += (pwr - idle_power_med) * dt

    energy = _integrate(np.array([[gen_power[j][0], gen_power[j][1] - idle_power_med] for j in range(gen_power.shape[0])]))
    d[m][pm] = energy

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, color=runs_cols)
ax.set_xticklabels(log_loader.model_order, rotation=10)
ax.set_title(f'Estimated Energy usage during Generation\n({dev} with quantization)')
ax.set_ylabel('Energy (J)')
plt.show()