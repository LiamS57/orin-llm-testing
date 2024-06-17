# General helper functions for generating with LLM models from HF.
# 
# Liam Seymour 6/17/24

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from torch import float16
from huggingface_hub import login

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

def load_model(model_name: str, bnb_conf=None):
    '''Load an LLM model from HF from the given string. Always loads to the GPU.'''
    print("Loading model: " + model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, device_map="auto", quantization_config=bnb_conf)
    tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
    return model, tokenizer

def load_model_quantized(model_name: str):
    '''Load an LLM model from HF with quantization enabled.'''
    return load_model(model_name=model_name, bnb_conf=BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_compute_dtype=float16))

def generate_from_input(model, tokenizer, input_text: str, max_new_tokens=64) -> str:
    '''Generates text from a given input, model, and tokenizer.'''
    model_inputs = tokenizer([input_text], return_tensors="pt").to("cuda")
    print("Generating tokens...")
    generated_ids = model.generate(**model_inputs, max_new_tokens=max_new_tokens, do_sample=True)
    print("Decoding tokens...")
    return tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]