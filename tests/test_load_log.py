import statlog
import os
import sys


if len(sys.argv) < 2:
    print('Not enough arguments!')
    exit(1)

json_str = ''
with open(os.path.abspath(sys.argv[1]), 'r') as fp:
    json_str = ''.join(fp.readlines())

log: statlog.Log = statlog.Log.from_json(json_str)
log.print(in_order=True)