import argparse

import polars as pl
from tqdm.auto import tqdm
from openai import OpenAI
import time
from pathlib import Path
import hashlib
import json

def parse_args():
    parser = argparse.ArgumentParser(description='Generate reviews using an LLM model')
    parser.add_argument('--infile', type=str, default='dataset_test.zstd.parquet',
                        help='Input parquet file containing test dataset')
    parser.add_argument('--outfile', type=str, default='dataset_test.zstd.parquet',
                        help='Output parquet file to save generated reviews')
    parser.add_argument('--model-name', type=str, default='openai/gpt-4o-2024-11-20',
                        help='Name or path of the model to use')
    parser.add_argument('--api-key-file', type=str, required=True,
                        help='File containing the OpenRouter API key')
    parser.add_argument('--completions-dir', type=str, default='completions',
                        help='Directory to store completion results')
    args = parser.parse_args()
    return args

args = parse_args()
args.col_name = args.model_name.split('/')[-1]
print(f'output column name: {args.col_name}')


# MODEL_NAME = "openai/gpt-4o-2024-11-20"
# MODEL_NAME = "anthropic/claude-3.5-sonnet"

with open(args.api_key_file, "r") as f:
    API_KEY = f.read().strip()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)


def chat_complete(client, model_name, messages):
    return client.chat.completions.create(
        model=model_name, messages=messages,
        extra_body={
            "temperature": 0.0,
        },
    )

completions_dir = Path(args.completions_dir) 
completions_dir.mkdir(exist_ok=True, parents=True)

# read test dataset
ds_test = pl.read_parquet(args.infile)

messages = ds_test.select(pl.col("messages")).to_series().to_list()

completions = []
for message in tqdm(messages):
    h = hashlib.md5(''.join(x['content'] for x in message).encode()).hexdigest()
    p = completions_dir / (args.col_name + '_' + str(h))
    if not p.exists():
        while True:
            try:
                completion = chat_complete(client, args.model_name, message)
                completions.append(completion.model_dump_json())
                with open(p, 'w') as f:
                    f.write(completion.model_dump_json())
                break
            except Exception as e:
                print(e)
                time.sleep(60)
    else:
        print('loading existing completion', p)
        with open(p, 'r') as f:
            completion = f.read()
            completions.append(completion)

completions = [json.loads(x) for x in completions]
reviews = [x['choices'][0]['message']['content'] for x in completions]

ds_test = ds_test.with_columns(pl.Series(name=args.col_name, values=reviews))

ds_test.write_parquet(args.outfile)