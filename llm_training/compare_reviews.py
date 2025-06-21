import argparse
import polars as pl
from tqdm.auto import tqdm
import re
import statistics
from openai import OpenAI
import time
from pathlib import Path
import hashlib
import json
import numpy as np

np.random.seed(10101010)
def parse_args():
    parser = argparse.ArgumentParser(description='Compare reviews using an LLM judge')
    parser.add_argument('--infile', type=str, default='dataset_test.zstd.parquet',
                        help='Input parquet file containing test dataset with generations for the contestants')
    parser.add_argument('--limit', type=int, default=0,
                        help='Limit number of comparisons for testing')
    parser.add_argument('--api-key-file', type=str, required=True,
                        help='File containing the OpenRouter API key')
    parser.add_argument('--model-name', type=str, default='openai/gpt-4o-2024-11-20',
                        help='Name of the judge model')
    parser.add_argument('--contestants', nargs=2, type=str, 
                        default=['Llama-OpenReviewer-8B', 'gpt-4o-2024-11-20'],
                        help='Two model names to compare reviews from')
    args = parser.parse_args()
    return args

args = parse_args()

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
SYSTEM_PROMPT_TEMPLATE = """You are an expert meta-reviewer for an AI conference. You will be provided with {n_expert_reviews} expert reviews and two additional reviews, review A and review B, all for the same paper. The expert reviews form a groundtruth of reviews. Your task is to determine whether review A or review B aligns better with the given expert reviews.

All reviewers were instructed to write reviews with the following sections:
{review_fields}

Think about how well each section of the reviews matches the corresponding section in the expert reviews, except for the summary section. For sections requiring a numerical rating, determine how well the numerical rating matches the numerical ratings of the expert reviews.

All reviews are delimited with XML tags.
Start your response with your thoughts about how well each section of Review A and Review B matches the corresponding section in the expert reviews. Then, provide your decision as either "Review A", "Review B", or "Tie".
"""

USER_PROMPT_TEMPLATE = """Expert reviews:
{expert_reviews}

Given the expert reviews above, judge which of the following reviews aligns better with the given expert reviews:

<review_a>
Review A:
{review_a}
</review_a>

<review_b>
Review B:
{review_b}
</review_b>
"""

def create_messages(review_fields, expert_reviews, review_a, review_b):
    expert_reviews_formatted = ""
    for i, review in enumerate(expert_reviews):
        expert_reviews_formatted += f"<expert_review_{i+1}>\n{review}\n</expert_review_{i+1}>\n\n"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(review_fields=review_fields, n_expert_reviews=len(expert_reviews))},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(expert_reviews=expert_reviews, review_a=review_a, review_b=review_b)},
    ]
    return messages

ds_test = pl.read_parquet(infile)
if args.limit:
    ds_test = ds_test.head(args.limit)

messages = []
contestants = []
for row in ds_test.rows(named=True):
    human_reviews = row['reviews']

    order = np.random.permutation(len(args.contestants))
    cs = [args.contestants[i] for i in order]
    contestants.append(cs)
    messages.append(create_messages(row['review_fields'], human_reviews, row[cs[0]], row[cs[1]]))

completions = []
for message in tqdm(messages):
    h = hashlib.md5(''.join(x['content'] for x in message).encode()).hexdigest()
    p = Path('completions_judge') / str(h)

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
responses = [x['choices'][0]['message']['content'] for x in completions]

decisions = []
for response in responses:
    # break
    response_end = response[-12:]
    decision = 'A' if 'A' in response_end else 'B' if 'B' in response_end else 'Tie'
    # assert decision in ['A', 'B', 'Tie']
    decisions.append(decision)

winners = []
for i, decision in enumerate(decisions):
    if decision == 'Tie':
        winner = 'Tie'
    else:
        winner = contestants[i][0 if decision == 'A' else 1]
    winners.append(winner)


from collections import Counter
c = Counter(winners)
print(c)

for contestant in args.contestants:
    print(contestant, c[contestant] / len(winners))
print('Tie', c['Tie'] / len(winners))

