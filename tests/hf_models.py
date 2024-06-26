# General helper functions for generating with LLM models from HF.
# 
# Liam Seymour 6/17/24

from huggingface_hub import login
from torch import float16
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, CONFIG_NAME
from transformers.utils.hub import cached_file

from multiprocessing import Process
from os import listdir
from os.path import expanduser
from shutil import rmtree

CACHE_DIR = expanduser('~/.cache/huggingface/hub/')
'''Cache directory for HF Hub'''

def login_by_token(token_file="access_token", token=None) -> bool:
    '''Attempts to login to HuggingFace Hub with a given token or token file.'''
    try:
        if token == None:
            print("Logging in with token file: " + token_file)
            with open(token_file, 'r') as tkf:
                login(token=tkf.readline())
        else:
            print("Logging in with token: " + token)
            login(token=token)
        return True
    except ValueError:
        print("Failed to validate token!")
    except OSError:
        print("Failed to open token file!")
    return False

def check_model_in_cache(model_name: str) -> bool:
    '''Checks whether or not a given model exists in the HF local cache.'''
    check = cached_file(
        model_name,
        CONFIG_NAME,
        _raise_exceptions_for_gated_repo=False,
        _raise_exceptions_for_missing_entries=False,
        _raise_exceptions_for_connection_errors=False,
        local_files_only=True
    )
    return check != None

def _dl_model_proc(model_name: str):
    # Note: there is probably a better way to do this. I'm just loading the model/tokenizer and 
    # immediately unloading them, since there is built-in downloading set up and models have different
    # files. However, I haven't seen any straightforward methods provided in the source for only
    # downloading the models without loading them.
    bnb_conf = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=float16)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", quantization_config=bnb_conf)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
    del model
    del tokenizer

def download_model(model_name: str):
    '''Downloads the given model from the HF Hub, unless it already exists in the HF local cache.
    
    Uses the multiprocessing library to isolate the loading process and release memory after downloading'''

    if not check_model_in_cache(model_name):
        print("Downloading model: " + model_name)
        pr = Process(target=_dl_model_proc, args=[model_name])
        pr.start()
        pr.join()
        del pr

def erase_cached_models():
    '''Removes all cached models in the HF local cache.'''
    for d in listdir(CACHE_DIR):
        if d.startswith("models--"):
            model_dir = CACHE_DIR + d
            print("Erasing " + model_dir)
            rmtree(model_dir, True)

def load_model(model_name: str, bnb_conf=None):
    '''Load an LLM model from HF from the given string. Always loads to the GPU.'''
    print("Loading model: " + model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", quantization_config=bnb_conf)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
    return model, tokenizer

def load_model_quantized(model_name: str):
    '''Load an LLM model from HF with quantization enabled.'''
    return load_model(model_name=model_name, bnb_conf=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=float16))

def generate_from_input(model, tokenizer, input_text: str, max_new_tokens=64) -> tuple[str, list]:
    '''Generates text from a given input, model, and tokenizer.
    Returns the generated text and a list of the generated tokens.'''
    model_inputs = tokenizer([input_text], return_tensors="pt").to("cuda")
    print("Generating tokens...")
    generated_ids = model.generate(**model_inputs, max_new_tokens=max_new_tokens, do_sample=True)
    print("Decoding tokens...")
    decoded = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    new_tokens = generated_ids[0][len(model_inputs['input_ids'][0]):]
    return decoded, new_tokens