import os
import json

print('Searching...')

log_paths = list()
for p, _, fs in list(os.walk('./out')):
    for f in fs:
        if f.startswith('log_') and f.endswith('json'):
            log_paths.append(os.path.join(p, f))

print(f'Found {len(log_paths)} logs\nValidating...')

bad_logs = list()
for path in log_paths:
    filename = os.path.basename(path)
    failed = False
    data = None
    with open(path, 'r') as fp:
        data = json.load(fp)
    if data == None:
        print(f'!!! {filename}: Failed to load JSON')
        failed = True

    stamps: list[str] = [x['value'] for x in data['timestamps']]
    for stamp in stamps:
        if stamp.endswith('_START'):
            end_stamp = stamp.rsplit('_', 1)[0] + '_END'
            if not end_stamp in stamps:
                print(f'!!! {filename}: {stamp} has no corresponding timestamp')
                failed = True
        if stamp.endswith('_END'):
            start_stamp = stamp.rsplit('_', 1)[0] + '_START'
            if not start_stamp in stamps:
                print(f'!!! {filename}: {stamp} has no corresponding timestamp')
                failed = True
    
    tokens = int(data['tokens_generated'])
    if tokens < 0:
        print(f'!!! {filename}: tokens_generated = {tokens}')
        failed = True

    if failed:
        bad_logs.append(path)


if len(bad_logs) > 0:
    if input(f'Remove {len(bad_logs)} bad logs? y/N: ').lower() == 'y':
        for path in bad_logs:
            os.remove(path)