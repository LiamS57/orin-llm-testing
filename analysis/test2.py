import numpy as np
import os
import sys

sys.path.insert(0, '../tests')
from statlog import Log

if len(sys.argv) != 2:
    print('Need to supply folder to pull data from!')
    exit(1)

in_folder = os.path.abspath(sys.argv[1])

print('Loading all log files from', in_folder)

# load from files into a list of logs associated with name fragments
loaded: list[tuple[list[str], Log]] = list()
for filename in os.listdir(in_folder):
    if filename.endswith('.json'):
        try:
            filepath = os.path.join(in_folder, filename)
            log_data = None
            with open(filepath, 'r') as fp:
                jstr = ''.join(fp.readlines())
                log_data = Log.from_json(jstr)
            
            name_data = filename[4:-5].split('_')
            #name_data.insert(0, name_data.pop()) # move suffix to the beginning of the name data

            loaded.append((name_data, log_data))
            #print(name_data)
        except:
            pass
print(f'Loaded {len(loaded)} files')

bleh: dict[str, int] = dict()
for info, _ in loaded:
    h = '_'.join([info[x] for x in range(len(info)) if x != 1])
    if h in bleh:
        bleh[h] += 1
    else:
        bleh[h] = 1

q = 0
nq = 0
for k, v in bleh.items():
    if 'no-quant' in k.split('_'):
        nq += 1
    else:
        q += 1
    if v < 5:
        print(f'{k}: {v}')
print(f'quant:{q}, no quant:{nq}')
