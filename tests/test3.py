import hf_models
from multiprocessing import Process
from time import sleep

models = [
    "EleutherAI/pythia-70m-deduped",
    "EleutherAI/pythia-160m-deduped",
    "EleutherAI/pythia-410m-deduped",
    "EleutherAI/pythia-1b-deduped",
    "EleutherAI/pythia-1.4b-deduped"
]

hf_models.login_by_token()
hf_models.erase_cached_models()
for m in models:
    hf_models.download_model(m)
sleep(10)

def run_generation_test(model_name: str):
    mdl, tk = hf_models.load_model_quantized(model_name)
    output = hf_models.generate_from_input(mdl, tk, "We are testing the ability of the model to")
    print(output)

for m in models:
    proc = Process(target=run_generation_test, args=[m])
    # here we put all of the model loading and usage in a separate process
    # this allows us to cleanly release all memory, both CPU and GPU
    proc.start()
    proc.join()
    sleep(5)