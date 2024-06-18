import hf_models
from jtop import jtop
from time import perf_counter

with jtop() as jetson:
    if jetson.ok():
        print(jetson.board['hardware'])

hf_models.login_by_token()

mem = list()
gmem = list()
def report_pt_mem(jetson: jtop):
    for proc in jetson.processes:
        if proc[9] == "pt_main_thread":
            global mem
            global gmem
            mem.append(proc[7] / 1024)
            gmem.append(proc[8] / 1024)

jetson = jtop(0.5)
jetson.attach(report_pt_mem)
jetson.start()
t_start = perf_counter()

mdl, tk = hf_models.load_model_quantized("EleutherAI/pythia-70m-deduped")
output = hf_models.generate_from_input(mdl, tk, "This is a test of the system")

t_end = perf_counter()
jetson.close()
print(f"\nOutput ({(t_end - t_start):.04f} s):")
print(output)
print("\nMem:")
print(mem)
print("GPU Mem:")
print(gmem)