from jtop import jtop
from time import sleep

def report_pt_mem(jetson: jtop):
    for proc in jetson.processes:
        if proc[9] == "pt_main_thread":
            # looks like these are provided in KB
            # based on what i can see in the jtop gui
            # converting them to MB for printing
            mem = proc[7] / 1024
            gmem = proc[8] / 1024
            print(f'{proc[9]} - MEM: {int(mem)} MB, GPU MEM: {int(gmem)} MB')

jetson = jtop(0.5)
jetson.attach(report_pt_mem)
jetson.start()

try:
    while True:
        sleep(10)
except KeyboardInterrupt:
    pass
jetson.close()