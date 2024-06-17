# Jetson Orin LLM Testing

Scripts/testing respository for testing HuggingFace LLM models on the Jetson AGX Orin Devkit.

## Setup

Due to peculiarities with JetPack, the installation process for the environment is much longer than the standard installation for HuggingFace transformers. This setup process has been divided into a set of scripts in case there are any errors, such that the process does not have to be restarted from the beginning after a failure midway.

For the default full setup process, run the following command:

```
$ ./scripts/setup/setup_all.sh
```

If a failure occurs during the process, you can make any necessary fixes and continue by manually running the individual [setup scripts](/scripts/setup/) in the order defined in the ```setup_all.sh``` script, starting from where the process left off.

## Testing

Before doing any testing, please ensure the environment has been set up properly as shown in [Setup](#setup).

If already properly set up, activate the virtual environment with the following command:

```
$ ./hf_env/bin/activate
```

Now the testing scripts located in [testing](/testing/) should work properly.