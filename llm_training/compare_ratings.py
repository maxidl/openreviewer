import numpy as np
import matplotlib.pyplot as plt
import polars as pl
from tqdm.auto import tqdm
import re
import statistics
from collections import defaultdict

rating_pattern = r"(#+ [Rr]ating)[\S\s]*"

ds_test = pl.read_parquet("data/dataset_test.zstd.parquet")

models = [
    'Llama-OpenReviewer-8B',
    'Llama-3.1-8B-Instruct',
    'Llama-3.1-70B-Instruct',
    'gpt-4o-2024-11-20',
    'claude-3.5-sonnet',
]

def get_rating(review):
    try:
        rating_text = re.search(rating_pattern, review).group(0)
        rating = int([c for c in rating_text if c.isdigit()][0])
    except Exception as e:
        print(e)
        # print(review)
        return 5 # This only affects a small number of reviews.
    return rating



ratings_humans = []
ratings_models = defaultdict(list)


results = defaultdict(list)


for row in ds_test.rows(named=True):
    # break
    human_reviews = row['reviews']

    ratings_human = [get_rating(review) for review in human_reviews]
    rating_human_avg = sum(ratings_human) / len(ratings_human)
    rating_human_median = statistics.median(ratings_human)

    ratings_humans.append(rating_human_avg)
    for model in models:
        rating = get_rating(row[model])
        ratings_models[model].append(rating)

        results[f'em_{model}'].append(rating in ratings_human)
        results[f'diff_{model}'].append(abs(rating - rating_human_avg) if rating is not None else None)
        results[f'diff_median_{model}'].append(abs(rating - rating_human_median) if rating is not None else None)


for model in models:
    print('\n==========')
    print(f'model: {model}')
    print(f'EM: {sum(results[f"em_{model}"])}')
    print(f'Diff avg: {sum(results[f"diff_{model}"]) / ds_test.shape[0]}')
    print(f'Diff median: {sum(results[f"diff_median_{model}"]) / ds_test.shape[0]}')

print('\n\n\n')

print(f'mean of human avg rating: {np.array(ratings_humans).mean()}')
for model in models:
    print('\n==========')
    print(f'model: {model}')
    print(f'mean rating: {np.array(ratings_models[model]).mean()}')
    print(f'std: {np.array(ratings_models[model]).std()}')




# def create_five_boxplots(array1, array2, array3, array4, array5, labels=None):
#     """
#     Creates a plot with 5 boxplots from provided numpy arrays.
    
#     Parameters:
#     array1, array2, array3, array4, array5: 1-dimensional numpy arrays containing the data
#     labels: list of strings for x-axis labels (optional, default None)
    
#     Returns:
#     None (displays the plot)
#     """
    
#     # Input validation
#     arrays = [array1, array2, array3, array4, array5]
    
#     # Check if inputs are numpy arrays
#     for i, arr in enumerate(arrays):
#         if not isinstance(arr, np.ndarray):
#             raise TypeError(f"Input {i+1} must be a numpy array")
        
#         # Check if arrays are 1-dimensional
#         if arr.ndim != 1:
#             raise ValueError(f"Input {i+1} must be a 1-dimensional array")
    
#     # Create figure and axis
#     fig, ax = plt.subplots(figsize=(10, 6))
    
#     # Create boxplots
#     box_plot = ax.boxplot(arrays, patch_artist=True)
    
#     # Customize boxplot colors
#     colors = ['lightblue', 'lightgreen', 'pink', 'lightgray', 'wheat']
    
#     for patch, color in zip(box_plot['boxes'], colors):
#         patch.set_facecolor(color)
    
#     # Set labels if provided
#     if labels is not None:
#         if len(labels) != 5:
#             raise ValueError("Number of labels must be 5")
#         ax.set_xticklabels(labels)
    
#     # Customize plot
#     ax.set_title('Boxplot Comparison')
#     ax.grid(True, linestyle='--', alpha=0.7)
    
#     # Show plot
#     plt.show()

# create_five_boxplots(np.array(ratings_gen), np.array(ratings_base), np.array(ratings_llama), np.array(ratings_gpt), np.array(ratings_sonnet), labels=['A', 'B', 'C', 'D', 'E'])