import argparse

import polars as pl

from vllm import LLM, SamplingParams


def parse_args():
    parser = argparse.ArgumentParser(description='Generate reviews using an LLM model')
    parser.add_argument('--infile', type=str, default='dataset_test.zstd.parquet',
                        help='Input parquet file containing test dataset')
    parser.add_argument('--outfile', type=str, default='dataset_test.zstd.parquet',
                        help='Output parquet file to save generated reviews')
    parser.add_argument('--model_name', type=str, default='maxidl/Llama-OpenReviewer-8B',
                        help='Name or path of the model to use')
    # parser.add_argument('--col_name', type=str, default='Llama-OpenReviewer-8B',
    #                     help='Column name for generated reviews in output file')
    args = parser.parse_args()
    return args

args = parse_args()
args.col_name = args.model_name.split('/')[-1]
print(f'output column name: {args.col_name}')

llm = LLM(model=args.model_name, dtype="bfloat16", tensor_parallel_size=4)
sampling_params = SamplingParams(temperature=0.0, top_p=0.9, n=1, max_tokens=4096)

# Define prompts
SYSTEM_PROMPT_TEMPLATE = """You are an expert reviewer for AI conferences. You follow best practices and review papers according to the reviewer guidelines.

Reviewer guidelines:
1. Read the paper: It’s important to carefully read through the entire paper, and to look up any related work and citations that will help you comprehensively evaluate it. Be sure to give yourself sufficient time for this step.
2. While reading, consider the following:
    - Objective of the work: What is the goal of the paper? Is it to better address a known application or problem, draw attention to a new application or problem, or to introduce and/or explain a new theoretical finding? A combination of these? Different objectives will require different considerations as to potential value and impact.
    - Strong points: is the submission clear, technically correct, experimentally rigorous, reproducible, does it present novel findings (e.g. theoretically, algorithmically, etc.)?
    - Weak points: is it weak in any of the aspects listed in b.?
    - Be mindful of potential biases and try to be open-minded about the value and interest a paper can hold for the community, even if it may not be very interesting for you.
3. Answer four key questions for yourself, to make a recommendation to Accept or Reject:
    - What is the specific question and/or problem tackled by the paper?
    - Is the approach well motivated, including being well-placed in the literature?
    - Does the paper support the claims? This includes determining if results, whether theoretical or empirical, are correct and if they are scientifically rigorous.
    - What is the significance of the work? Does it contribute new knowledge and sufficient value to the community? Note, this does not necessarily require state-of-the-art results. Submissions bring value to the community when they convincingly demonstrate new, relevant, impactful knowledge (incl., empirical, theoretical, for practitioners, etc).
4. Write your review including the following information: 
    - Summarize what the paper claims to contribute. Be positive and constructive.
    - List strong and weak points of the paper. Be as comprehensive as possible.
    - Clearly state your initial recommendation (accept or reject) with one or two key reasons for this choice.
    - Provide supporting arguments for your recommendation.
    - Ask questions you would like answered by the authors to help you clarify your understanding of the paper and provide the additional evidence you need to be confident in your assessment.
    - Provide additional feedback with the aim to improve the paper. Make it clear that these points are here to help, and not necessarily part of your decision assessment.

Your write reviews in markdown format. Your reviews contain the following sections:

# Review

{review_fields}

Your response must only contain the review in markdown format with sections as defined above.
"""

USER_PROMPT_TEMPLATE = """Review the following paper:

{paper_text}
"""



def create_messages(review_fields, paper_text):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(review_fields=review_fields)},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(paper_text=paper_text)},
    ]
    return messages


# read test dataset
ds_test = pl.read_parquet(args.infile)

# create messages to send to the model
if not 'messages' in ds_test.columns:
    messages = []
    for row in ds_test.rows(named=True):
        messages.append(create_messages(row["review_fields"], row["paper_text"]))

    ds_test = ds_test.with_columns(pl.Series(name="messages", values=messages))

else:
    messages = ds_test.select(pl.col("messages")).to_series().to_list()
# run model

output = llm.chat(messages, sampling_params=sampling_params)

# add outputs to dataset and save
reviews = [x.outputs[0].text for x in output]
ds_test = ds_test.with_columns(pl.Series(name=args.col_name, values=reviews))

ds_test.write_parquet(args.outfile)
