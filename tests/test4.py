import hf_models
from statlog import Log

from datetime import datetime
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
import os
from time import sleep

models = [
    "EleutherAI/pythia-70m-deduped",
    "EleutherAI/pythia-160m-deduped",
    "EleutherAI/pythia-410m-deduped",
    "EleutherAI/pythia-1b-deduped",
    "EleutherAI/pythia-1.4b-deduped"
]
input_data = "We are testing the ability of the model to"

output_dir = os.path.abspath('./out/')
date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')

#hf_models.login_by_token()
#hf_models.erase_cached_models()
print("Downloading models...")
for m in models:
    hf_models.download_model(m)
print("Download(s) complete")
sleep(3)


# The following function is used in a separate process to run the generation test.
# Add any desired testing to this function to ensure it is tested on each model
def run_generation_test(model_name: str, in_data, conn: Connection):
    # TEST BEGIN

    conn.send('Model and tokenizer loading started')
    mdl, tk = hf_models.load_model_quantized(model_name)
    conn.send('Model and tokenizer loading finished')

    conn.send('Output generation started')
    output = hf_models.generate_from_input(mdl, tk, in_data)
    conn.send('Output generation finished')

    # TEST END
    conn.close()


print("Beginning tests of each model")
for m in models:
    print(f'\nRunning test on {m}')
    test_log = Log()
    test_log.begin()
    sleep(5) # buffer time to see power before generation

    # here we put all of the model loading and usage in a separate process
    # this allows us to cleanly release all memory, both CPU and GPU
    # additionally, a pipe is used to send back timestamped messages for the log
    msg_recv, msg_send = Pipe()
    proc = Process(target=run_generation_test, args=[m, input_data, msg_send])
    proc.start()
    while proc.is_alive():
        if msg_recv.poll():
            test_log.add_timestamp(str(msg_recv.recv()))
    proc.join()
    if not msg_send.closed:
        msg_send.close()
    msg_recv.close()

    sleep(5) # buffer time to see power after generation
    test_log.end()
    print(f'Test on {m} complete')

    # save the log to a file for analysis
    outfilename = '_'.join(['log', date_str, m.split('/')[-1] + '.json'])
    outfilepath = os.path.join(output_dir, outfilename)
    print(f'Saving log to {outfilepath}')
    json_str = test_log.to_json()
    with open(outfilepath, 'w') as fp:
        fp.write(json_str)