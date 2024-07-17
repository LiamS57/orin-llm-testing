import os
import sys

import log_loader

if len(sys.argv) != 2:
    print('Need to supply folder to pull data from!')
    exit(1)

in_folder = os.path.abspath(sys.argv[1])
data = log_loader.load_logs_from_folder(in_folder)

def m_name(param):
    return f'pythia-{param}-deduped'

for d in data.with_and_without_tags([m_name('70m'), 'orin-nano-4gb'], ['no-quant']):
    print(d._tags)

power_dict = {
    'agx-orin-32gb': ['MAXN', '40W', '30W', '15W'],
    'orin-nx-16gb': ['MAXN', '25W', '15W', '10W'],
    'orin-nx-8gb': ['MAXN', '20W', '15W', '10W'],
    'orin-nano-8gb': ['15W', '7W'],
    'orin-nano-4gb': ['10W', '7W-AI', '7W-CPU']
}