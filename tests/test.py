import hf_models

hf_models.login_by_token()
mdl, tk = hf_models.load_model_quantized("EleutherAI/pythia-1.4b-deduped")
print(hf_models.generate_from_input(mdl, tk, "This is a test of the system"))