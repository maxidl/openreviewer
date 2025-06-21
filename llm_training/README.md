# LLM Training
Training the OpenReviewer model.
Model training is done using [Axolotl](https://github.com/axolotl-ai-cloud/axolotl).

## Environment

```
conda create -n ordc python=3.10
conda install pytorch pytorch-cuda=12.4 -c pytorch -c nvidia
conda install nvidia/label/cuda-12.4.0::cuda-toolkit

```

See [axolotl#installation](https://github.com/axolotl-ai-cloud/axolotl#installation) for further environment setup.


## Preparing Data

Use `prepare_data.py` to preprocess the dataset created from openreview.

It currently does the following preprocessing steps:
* split the md text into main and appendix
* plot the main text length distribution
* filter based on paper length
* filter based on review length
* plot the review length distribution
* filter based on reviewer confidence
* format reviews
* split into train/test datasets

Then, use `pretokenize.py` to tokenize the data for model training. This is also the place to define the system and user prompt.


## Training

The config files used are
* `acc_config.py` for the accelerate config.
* `fft-llama31-8B-liger-ds.yaml` for the axolotl training config.

The training is launched using the `finetune.slurm` script.


## Evaluation

### Generating reviews on test dataset
`generate.py` runs generation on the test dataset using vllm.
`generate_openrouter.py` runs generation on the test dataset via openrouter.

The scripts are setup to work with 4 GPUs by default. For the openrouter script does not require a GPU.
For the OpenReviewer paper we run generations using the following commands:
```
python generate.py # default
python generate.py --model_name "meta-llama/Llama-3.1-8B-Instruct"
python generate.py --model_name "meta-llama/Llama-3.1-70B-Instruct"
python generate_openrouter.py --api-key-file ~/openrouter.api_key
python generate_openrouter.py --api-key-file ~/openrouter.api_key --
```

Caveat: If you use the same in/outfile, only run one at a time.

### Matching recommendations
`compare_ratings.py` compares the ratings of the generated reviews to the human ratings and prints results.

### arena style evaluation
`compare_reviews.py` compares the generated reviews of two models using an LLM judge and prints results (winrates).

### Plotting
`plot_winrates.py` plots the winrates of the OpenReviewer model against other models.