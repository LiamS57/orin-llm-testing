# Testing Scripts

## Main Testing Script

To run the main testing script, use the following command:

```
python run_tests.py
```

This script redownloads all the models defined in **models.txt** and runs several iterations of tests on each model using the input provided in input.txt. It saves logs for each test into an output folder, which has a nested folder structure based on the date/time that the tests were started. A sample of this structure follows:

```
out
    2024-06-25_150000
        log_pythia-70m-deduped_1.json
        log_pythia-160m-deduped_1.json
        ...
```

By default, this script runs 5 iterations of each test, loading each model with 4-bit quantization. This behavior can be changed with the following options:

```
python run_tests.py --iterations=3 --no-quant
```

Additionally, a suffix can be added to mark test logs if needed. To use a suffix, use the ```--suffix=info``` option. This will change the log filenames to "log_pythia-70m-deduped_1_info.json".

For more usage information, use the ```--help``` option.

## Writing a Custom Test Script



### Helper libraries

[```hf_models.py```](./hf_models.py) provides helper functions for simplifying the usage of HuggingFace LLM models. These functions can reduce text generation to three lines of code:

```python
import hf_models
mdl, tk = hf_models.load_model_quantized("EleutherAI/pythia-70m-deduped")
output, _ = hf_models.generate_from_input(mdl, tk, "Hello there! My name is")
```

[```statlog.py```](./statlog.py) provides a timestamp-based logging system using JTop to log several stats of the Jetson. Once an instance of the log begins, it takes continuous readings of Jetson stats until stopped. Timestamps can be added at specific points during a test to signify when an event occurs. The log can be exported to/imported from JSON format files for storage/transfer off the Jetson device (i.e. before a reflash).

## Additional Information

### Increasing JTop sample rate

At installation, the minimum sample time for the internal JTop service is 500ms, regardless of what the interval is set to in the scripts. To change this, you must edit the systemd service file (jtop.service) and re-enable/restart it.

For example, to change the rate to 100ms, adjust the jtop.service file (located at /etc/systemd/system/jtop.service) so that the ```ExecStart``` line looks like this:
```
ExecStart=/usr/local/bin/jtop --force -r 100
```
Afterwards, simply re-enable and restart the service.