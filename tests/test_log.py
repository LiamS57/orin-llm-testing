import statlog

# run a 15 second log and print the log entries
log = statlog.run_blocking(15)

print(f'Start time: {log.time_log_start:.4f} s')
print(f'End time: {log.time_log_end:.4f} s')

print('RAM Usage:')
for pid, mem_list in log.memory_ram.items():
    print(f'  PID: {pid}')
    for entry in mem_list:
        print(f'    ({entry.time:.4f} s): {int(entry.value / 1000)} MB')

print('GPU Mem Usage:')
for pid, mem_list in log.memory_gpu.items():
    print(f'  PID: {pid}')
    for entry in mem_list:
        print(f'    ({entry.time:.4f} s): {int(entry.value / 1000)} MB')

print('Power Usage:')
for entry in log.power:
    print(f'  ({entry.time:.4f} s): {entry.value} W')

print('Timestamps:')
for entry in log.timestamps:
    print(f'  ({entry.time:.4f} s): {entry.value}')