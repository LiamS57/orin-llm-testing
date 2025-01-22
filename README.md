# Jetson Orin LLM Testing

Scripts/testing respository for testing HuggingFace LLM models on the Jetson AGX Orin Devkit.

## Setup

Due to peculiarities with JetPack, the installation process for the environment is much longer than the standard installation for HuggingFace transformers. This setup process has been divided into a set of scripts in case there are any errors, such that the process does not have to be restarted from the beginning after a failure midway.

For every device configuration, the setup process is as follows:

1. Flash the desired device configuration to the Jetson Orin Devkit

   NOTE: This step can be skipped if testing on a specific Jetson Orin device (i.e., the Orin NX 16GB)

2. Perform the full setup process using the following command:

   ```
   $ ./scripts/setup/setup_all.sh
   ```

If a failure occurs during the process, you can make any necessary fixes and continue by manually running the individual [setup scripts](/scripts/setup/) in the order defined in the ```setup_all.sh``` script, starting from where the process left off.

## Testing

Before doing any testing, please ensure the environment has been set up properly as shown in [Setup](#setup).

If already properly set up, activate the virtual environment with the following command:

```
$ source ./hf_env/bin/activate
```

Now the testing scripts located in [tests](/tests/) should work properly.

## Citation

If you would like to use this utility for further research, please use the following BibTeX citation to reference our paper:

```
@misc{seymour2024largelanguagemodelssmall,
      title={Large Language Models on Small Resource-Constrained Systems: Performance Characterization, Analysis and Trade-offs}, 
      author={Liam Seymour and Basar Kutukcu and Sabur Baidya},
      year={2024},
      eprint={2412.15352},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2412.15352}, 
}
```
