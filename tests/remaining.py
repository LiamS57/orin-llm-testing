import os

# important test naming info
def m_name(param):
    return f'pythia-{param}-deduped'
device_order = ['agx-orin-devkit', 'agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', '50W', 'MAXN']
model_order = [m_name('70m'), m_name('160m'), m_name('410m'), m_name('1.4b')]
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
for p, _, fs in list(os.walk('./out')):
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
    
    existing.append(tags)

existing.sort()


# check

print('\nStill needing:')

for dev in device_order:
    print(f'  {dev}:')
    pms = device_pm_dict[dev]
    for pm in pms:
        model_lines = list()
        for model in model_order:
            found = [x for x in existing if x[0] == dev and x[1] == pm and x[2] == model]

            quant_left = max_iterations
            no_quant_left = max_iterations

            for f in found:
                if 'no-quant' in f:
                    no_quant_left -= 1
                else:
                    quant_left -= 1
            
            # printing
            left_text = list()
            if quant_left > 0:
                left_text.append(f'quant: {quant_left}')
            if no_quant_left > 0:
                left_text.append(f'no-quant: {no_quant_left}')
            if len(left_text) > 0:
                left_text.insert(0, f'{model}:')
                model_lines.append('  '.join(left_text))

        if len(model_lines) > 0:
            print(f'    {pm}:')
            for line in model_lines:
                print(f'      {line}')
