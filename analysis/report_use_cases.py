from math import isnan
import numpy as np
import os
import json

in_folder = os.path.abspath('../tests/out')

# important test naming info
def m_name(param):
    return f'pythia-{param}-deduped'
device_order = ['agx-orin-devkit', 'agx-orin-32gb', 'orin-nx-16gb', 'orin-nx-8gb', 'orin-nano-8gb', 'orin-nano-4gb']
pm_order = ['7W', '7W-AI', '7W-CPU', '10W', '15W', '20W', '25W', '30W', '40W', '50W', 'MAXN']
model_params = ['70m', '160m', '410m', '1.4b']
model_order = [m_name(x) for x in model_params]
device_pm_dict = {
    'agx-orin-devkit': ['MAXN', '50W', '30W', '15W'],
    'agx-orin-32gb': ['MAXN', '40W', '30W', '15W'],
    'orin-nx-16gb': ['MAXN', '25W', '15W', '10W'],
    'orin-nx-8gb': ['MAXN', '20W', '15W', '10W'],
    'orin-nano-8gb': ['15W', '7W'],
    'orin-nano-4gb': ['10W', '7W-AI', '7W-CPU']
}


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

def is_within_times(t, t1s, t1e, t2s, t2e):
    return (t1s <= t <= t1e) or (t2s <= t <= t2e)

def load_log(path: str) -> dict:
    with open(path, 'r') as fp:
        return json.load(fp)
    
def integrate(lst: list[tuple]) -> float:
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


# get all logs
print('Searching...')

log_paths = list()
for p, _, fs in list(os.walk(in_folder)):
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
    tags.append(path) # add to the end
    
    existing.append(tags)

existing.sort()


accuracy = dict()
with open('accuracy.json', 'r') as fp:
    af = json.load(fp)

    parsed = dict()
    for llm in model_order:
        parsed[llm] = dict()
    for k, v in af.items():
        llmpath, prec = k.split(',')
        llm = llmpath.split('/')[-1]
        if llm in model_order:
            parsed[llm][prec] = v

    for llm in model_order:
        accuracy[llm] = dict()
        accuracy[llm]['nq'] = parsed[llm]['fp16'][0] * 100.0
        accuracy[llm]['q'] = parsed[llm]['fp4'][0] * 100.0


#-- create results dict --#

results = list()
for dev in device_order:
    for pm in device_pm_dict[dev]:
        for llm in model_order:
            iters_nq = [x for x in existing if dev in x and pm in x and llm in x and 'no-quant' in x]
            iters_q = [x for x in existing if dev in x and pm in x and llm in x and ('no-quant' not in x)]

            for iters, q in zip([iters_q, iters_nq], ['q', 'nq']):
                lats = list()
                mems = list()
                pows = list()
                energies = list()
                for log in [load_log(x[-1]) for x in iters]:
                    t_load_start, t_load_end = get_times_between_stamps(log, 'MODEL_LOAD')
                    t_gen_start, t_gen_end = get_times_between_stamps(log, 'GENERATE')
                    lats.append((t_load_end - t_load_start) + (t_gen_end - t_gen_start))

                    series_gpu = log['memory_gpu']
                    pid_gpu = list(series_gpu.keys())[0]
                    series_ram = log['memory_ram']
                    pid_ram = list(series_gpu.keys())[0]
                    assert len(series_gpu) == 1
                    assert len(series_ram) == 1
                    assert pid_gpu == pid_ram
                    i_gpu = [x['value'] for x in series_gpu[pid_gpu] if is_within_times(x['time'], t_load_start, t_load_end, t_gen_start, t_gen_end)] # gpu memory for this iteration
                    i_ram = [x['value'] for x in series_ram[pid_ram] if is_within_times(x['time'], t_load_start, t_load_end, t_gen_start, t_gen_end)] # cpu memory for this iteration
                    i_pk_gpu = np.max(i_gpu) / 1024.0 # peak gpu memory for this iteration
                    i_pk_ram = np.max(i_ram) / 1024.0 # peak cpu memory for this iteration
                    mems.append(i_pk_ram + i_pk_gpu)

                    series_pwr = [(x['time'], x['value']) for x in log['power'] if t_gen_start <= x['time'] <= t_gen_end]
                    pk_pwr = np.max(series_pwr, axis=0)[1]
                    pows.append(pk_pwr)

                    en = integrate(series_pwr)
                    energies.append(en)

                res_entry = dict()
                res_entry['conf'] = f'{dev},{pm},{llm},{q}'
                res_entry['lat'] = np.median(lats)
                res_entry['mem'] = np.median(mems)
                res_entry['pwr'] = np.median(pows)
                res_entry['enr'] = np.median(energies)
                res_entry['acc'] = accuracy[llm][q]
                results.append(res_entry)


#-- begin --#
# results.sort(key=lambda x: x['mem'])
# for p in results:
#     print(p)
# exit()
print('Extrema:')
for k in ['lat', 'mem', 'pwr', 'enr', 'acc']:
    res = [x[k] for x in results if not isnan(x[k])]
    print(f'  {k} -> min: {np.min(res)}, max: {np.max(res)}')
print('\n\n')


uc1 = [[45, 30, 15], # below this power
       [40, 30, 20]] # below this lat
uc2 = [[240, 240, 120], # below this energy
       [1400, 700, 700]] # below this memory
uc3 = [[36, 42, 48], # above this acc
       [800, 1200, 2000]] # below this memory


print('Use Case #1')
uc1_sol = list()
for uc1_pwr_max, uc1_lat_max in zip(uc1[0], uc1[1]): # below this power, above this acc
    results_uc1 = [x for x in results if x['pwr'] <= uc1_pwr_max and x['lat'] <= uc1_lat_max]
    results_uc1.sort(key=lambda x: -x['acc']) # highest accuracy
    if len(results_uc1):
        print(f'   <{uc1_pwr_max}W, <{uc1_lat_max} s -> (out of {len(results_uc1)}) {results_uc1[0]}')
        uc1_sol.append(results_uc1[0]['conf'])
        pwr_other = [x["pwr"] for x in results_uc1]
        acc_other = [x["acc"] for x in results_uc1]
        # print(f'       extremes of results: pwr: {np.min(pwr_other)}-{np.max(pwr_other)}, acc: {np.min(acc_other)}-{np.max(acc_other)}')
    else:
        print(f'   <{uc1_pwr_max}W, <{uc1_lat_max} s -> No Results')

input()
print('Use Case #2')
uc2_sol = list()
for uc2_enr_max, uc2_mem_max in zip(uc2[0], uc2[1]): # below this energy, below this memory
    results_uc2 = [x for x in results if x['enr'] <= uc2_enr_max and x['mem'] <= uc2_mem_max]
    results_uc2.sort(key=lambda x: x['lat']) # lowest latency
    if len(results_uc2):
        print(f'   <{uc2_enr_max}J, <{uc2_mem_max}MB -> (out of {len(results_uc2)}) {results_uc2[0]}')
        uc2_sol.append(results_uc2[0]['conf'])
        enr_other = [x["enr"] for x in results_uc2]
        mem_other = [x["mem"] for x in results_uc2]
        # print(f'       extremes of results: enr: {np.min(enr_other)}-{np.max(enr_other)}, mem: {np.min(mem_other)}-{np.max(mem_other)}')
    else:
        print(f'   <{uc2_enr_max}J, <{uc2_mem_max}MB -> No Results')

input()
print('Use Case #3')
uc3_sol = list()
for uc3_acc_min, uc3_mem_max in zip(uc3[0], uc3[1]): # above this acc, below this memory
    results_uc3 = [x for x in results if x['acc'] >= uc3_acc_min and x['mem'] <= uc3_mem_max]
    results_uc3.sort(key=lambda x: x['lat']) # lowest latency
    if len(results_uc3) > 0:
        print(f'   >{uc3_acc_min}%, <{uc3_mem_max}MB -> (out of {len(results_uc3)}) {results_uc3[0]}')
        uc3_sol.append(results_uc3[0]['conf'])
        acc_other = [x["acc"] for x in results_uc3]
        mem_other = [x["mem"] for x in results_uc3]
        # print(f'       extremes of results: acc: {np.min(acc_other)}-{np.max(acc_other)}, mem: {np.min(mem_other)}-{np.max(mem_other)}')
    else:
        print(f'   >{uc3_acc_min}%, <{uc3_mem_max}MB -> No Results')