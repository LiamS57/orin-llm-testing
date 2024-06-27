# Primary testing script for running generation tests on LLMs
# 
# Models are loaded from 'models.txt', and input is loaded from 'input.txt'.
# Use 'run_tests.py --help' for a summary of usage options.
# 
# Liam Seymour 6/24/24


# pre-argument-checking imports
import os
import sys

# set up default variables
models_filepath = 'models.txt'
input_filepath = 'input.txt'
iterations = 5
output_dir = 'out'
suffix = ''
opt_no_erase = False
opt_no_quant = False

# function for printing the usage text
def print_usage_help():
    print("Usage: run_tests.py [--OPTION[=...]]...\n")
    print("  --help             Shows this help")
    print("  --modelsfile=...   Uses the given file to look for LLM model names (Default: ./models.txt)")
    print("  --inputfile=...    Uses the given file as input for text generation (Default: ./input.txt)")
    print("  --iterations=...   Sets the number of iterationsto repeat individual tests (Default: 5)")
    print("  --no-erase         Prevents the script from erasing previously cached models")
    print("  --no-quant         Forces the models to be loaded without quantization")
    print("  --outputdir=...    Outputs log files to the given directory (Default: ./out)")
    print("  --suffix=...       Adds the given suffix to the generated log files")
    print("\nExamples:")
    print("  run_tests.py --iterations=3 --suffix=fewer-iterations")
    print("  run_tests.py --no-erase --outputdir=./logs\n")

# process command-line arguments
for arg in sys.argv[1:]:
    # non-key-value args
    match arg:
        case "--help":
            print_usage_help()
            exit(0)
        case "--no-erase":
            opt_no_erase = True
        case "--no-quant":
            opt_no_quant = True
        case _:
            # key-value args
            tmp = arg.split('=')
            if len(tmp) != 2:
                print(f'Unknown option: {arg}\n')
                print_usage_help()
                exit(1)
            opt_var = tmp[0]
            opt_data = tmp[1]
            match opt_var:
                case "--modelsfile":
                    models_filepath = os.path.abspath(opt_data)
                case "--inputfile":
                    input_filepath = os.path.abspath(opt_data)
                case "--iterations":
                    if int(opt_data) < 1:
                        print(f'Too few iterations, cannot do negative or zero iterations!')
                        exit(1)
                    iterations = int(opt_data)
                case "--outputdir":
                    output_dir = os.path.abspath(opt_data)
                case "--suffix":
                    suffix = opt_data
                case _:
                    print(f'Unknown option: {opt_var}\n')
                    print_usage_help()
                    exit(1)


# post-argument-checking imports (to prevent time delay)
import hf_models
from statlog import Log

from datetime import datetime
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from pathlib import Path
from time import sleep

# set up datestring for subfolder
date_str = datetime.now().strftime('%Y-%m-%d_%H%M%S')

# load models from the list of names in the given file
print("Loading model names...", end='')
models = []
with open(models_filepath, 'r') as model_file:
    for m in model_file.readlines():
        models.append(m.rstrip('\n'))
print(f'Got {len(models)} models')

# load input data (text) from the given input file
print("Loading input text...", end='')
input_data = ""
with open(input_filepath, 'r') as input_file:
    input_data = '\n'.join(input_file.readlines())
print(f'Got {len(input_data)} characters')


# login to huggingface hub (for access to gated models)
hf_models.login_by_token()

# ensure models are loaded in the cache
# we do not want to benchmark network download times!
if not opt_no_erase:
    print("Erasing cached models...")
    hf_models.erase_cached_models()
print("Downloading models...")
for m in models:
    hf_models.download_model(m)
print("Download(s) complete")
sleep(3)


# The following function is used in a separate process to run the generation test.
# Add/change any desired testing functionality in this function to ensure it is tested on each model!
def _individual_test(model_name: str, in_data, conn: Connection, do_quantize: bool):
    '''Test method content, performed on a separate process.'''
    # Change any content within TEST BEGIN and TEST END to change the testing behavior!
    # TEST BEGIN

    conn.send('IDLE_START')
    print('Running idle period for power baseline')
    sleep(15)
    conn.send('IDLE_END')

    sleep(3) # buffer time

    conn.send('MODEL_LOAD_START')
    mdl = None
    tk = None
    if do_quantize:
        mdl, tk = hf_models.load_model_quantized(model_name)
    else:
        mdl, tk = hf_models.load_model(model_name)
    conn.send('MODEL_LOAD_END')

    sleep(3) # buffer time

    conn.send('GENERATE_START')
    output, new_tokens = hf_models.generate_from_input(mdl, tk, in_data)
    conn.send('GENERATE_END')

    # TEST END
    conn.send(f'TOKENS:{len(new_tokens)}')
    print(output)
    conn.close()


# run tests
for m in models:
    for i in range(iterations):
        m_subname = m.split('/')[-1]
        print(f'\n### Beginning test of {m_subname} ({i+1}/{iterations})')

        test_log = Log()
        test_log.begin(interval=0.1)
        sleep(3) # buffer time

        # here we put all of the model loading and usage in a separate process
        # this allows us to cleanly release all memory, both CPU and GPU
        # additionally, a pipe is used to send back timestamped messages for the log
        msg_recv, msg_send = Pipe()
        proc = Process(target=_individual_test, args=[m, input_data, msg_send, not opt_no_quant])
        proc.start()
        while proc.is_alive():
            if msg_recv.poll():
                message = str(msg_recv.recv())
                test_log.add_timestamp(message)
                msg_var = message.split(':')
                if len(msg_var) > 1:
                    if msg_var[0] == 'TOKENS':
                        test_log.tokens_generated = int(msg_var[1])
        proc.join()
        if not msg_send.closed:
            msg_send.close()
        msg_recv.close()

        sleep(3) # buffer time
        test_log.end()
        print(f'### Finished test of {m_subname} ({i+1}/{iterations})')

        # save the log to a file for analysis
        outfolder = os.path.join(os.path.abspath(output_dir), date_str)
        Path(outfolder).mkdir(parents=True, exist_ok=True)
        log_name_parts = ['log', m_subname, str(i+1)]
        if opt_no_quant:
            log_name_parts.append('no-quant')
        if len(suffix) > 0:
            log_name_parts.append(suffix)
        outfilename = '_'.join(log_name_parts) + '.json'
        outfilepath = os.path.join(outfolder, outfilename)
        print(f'### Saving log to {outfilepath}')
        json_str = test_log.to_json()
        with open(outfilepath, 'w') as fp:
            fp.write(json_str)