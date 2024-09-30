import os
import sys

import log_loader

if len(sys.argv) != 2:
    print('Need to supply folder to pull data from!')
    exit(1)

in_folder = os.path.abspath(sys.argv[1])
data = log_loader.load_logs_from_folder(in_folder)


for d in data.with_and_without_tags([log_loader.m_name('70m'), 'orin-nano-4gb'], ['no-quant']):
    print(d._tags)