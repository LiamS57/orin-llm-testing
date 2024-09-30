import json
import matplotlib.pyplot as plt
from matplotlib import cm
import pandas as pd

def m_name(param):
    return f'pythia-{param}-deduped'
model_params = ['70m', '160m', '410m', '1b', '1.4b']
model_order = [m_name(x) for x in model_params]

data:dict = None
with open('accuracy.json', 'r') as fp:
    data = json.load(fp)

parsed = dict()
for m in model_order:
    parsed[m] = dict()
for k, v in data.items():
    llmpath, prec = k.split(',')
    llm = llmpath.split('/')[-1]
    parsed[llm][prec] = v


# print(parsed)
d = dict()
for m in model_order:
    d[m] = dict()
    d[m]['No Quantization'] = parsed[m]['fp16'][0] * 100.0
    d[m]['4-bit Quantization'] = parsed[m]['fp4'][0] * 100.0

df = pd.DataFrame(d).T
print(df)

fig, ax = plt.subplots()
df.plot(kind='bar', ax=ax, colormap=cm.tab20)
ax.set_xticklabels(model_params, rotation=0)
ax.set_xlabel('Pythia Model')
ax.set_ylabel('Accuracy (%)')
ax.set_ybound(lower=0, upper=100)
plt.show()