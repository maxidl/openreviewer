# import os
# os.environ["TOKENIZERS_PARALLELISM"] = "false"
import datasets as hfds
import polars as pl
import transformers
from tqdm.auto import tqdm
from pathlib import Path

model_name = "meta-llama/Llama-3.1-8B-Instruct"
OUTPUT_DIR = Path("data/data-llama31-8b")
OUTPUT_DIR.mkdir(exist_ok=True)

df_train = pl.read_parquet("data/dataset_train.zstd.parquet")
df_test = pl.read_parquet("data/dataset_test.zstd.parquet")

tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)

ds_train = hfds.Dataset.from_polars(df_train)
ds_test = hfds.Dataset.from_polars(df_test)
ds = hfds.DatasetDict({"train": ds_train, "test": ds_test})

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

# create messages
def create_messages(row):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(review_fields=row['review_fields'])},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(paper_text=row['paper_text'])},
        {"role": "assistant", "content": row['review']}
    ]
    return messages

ds = ds.map(lambda row: {'messages': create_messages(row)})
ds = ds.map(lambda row: {'messages_len': len(row['messages'])})


ds = ds.map(lambda x: {'input_ids_prompt': tokenizer.apply_chat_template(x['messages'][:-1], add_generation_prompt=True)})
ds = ds.map(lambda x: {'input_ids': tokenizer.apply_chat_template(x['messages'])})
ds = ds.map(lambda x: {'attention_mask': [1] * len(x['input_ids'])})
ds = ds.map(lambda x: {'labels': [-100] * len(x['input_ids_prompt']) + x['input_ids'][len(x['input_ids_prompt']):]})

ds.save_to_disk(OUTPUT_DIR / "dataset_tokenized")
ds = ds.select_columns(['input_ids', 'attention_mask', 'labels'])

ds['train'].to_parquet(OUTPUT_DIR / "train_full.parquet")
ds['train'].select(range(10_000)).to_parquet(OUTPUT_DIR / "train_10k.parquet")
ds['train'].select(range(1_000)).to_parquet(OUTPUT_DIR / "train_1k.parquet")
