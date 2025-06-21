import matplotlib.pyplot as plt
import matplotlib
import numpy as np

params = {
    # Use LaTeX to write all text
    "axes.labelsize": 10,
    "font.size": 10,
    'font.weight': 'normal',
    # Make the legend/label fonts a little smaller
    "legend.fontsize": 10,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    # "ylabel.fontsize": 8,
    'savefig.pad_inches': 0
}

plt.rcParams.update(params)

plt.rcParams.update({'font.size': 12, })
# matplotlib.rcParams["font.size"] = "10"

# Data from experiments
models = ['GPT-4o (2024-11-20)', 'Claude-3.5-Sonnet', 'Llama-3.1-70B-Inst.', 'Llama-3.1-8B-Instr.']
or_wins = [60, 69, 76, 70]
ties = [10, 12, 12, 20]
or_loses = [30, 19, 12, 10]

# Indices and x-ticks
num_models = len(models)
indices = np.arange(num_models)
x_ticks = [0, 25, 50, 75, 100]

# Bar plot
fig, ax = plt.subplots(figsize=(5, 2.5))

# Horizontal bar sections
# ax.barh(indices, or_wins, color='#5DADE2', label='or wins', edgecolor="black")
# ax.barh(indices, ties, left=or_wins, color='#AED6F1', label='Tie', edgecolor="black")
# ax.barh(indices, or_loses, left=np.array(or_wins) + np.array(ties), color='#D6EAF8', label='or Loses', edgecolor="black")
ax.barh(indices, or_wins, color='#1976D2', label='OpenReviewer wins', edgecolor="black")
ax.barh(indices, ties, left=or_wins, color='#42A5F5', label='Tie', edgecolor="black")
ax.barh(indices, or_loses, left=np.array(or_wins) + np.array(ties), color='#E3F2FD', label='OpenReviewer loses', edgecolor="black")


# Add text inside bars
for i, (win, tie, lose) in enumerate(zip(or_wins, ties, or_loses)):
    ax.text(win / 2, i, f"{win}%", ha="center", va="center", color="white", fontsize=10)
    ax.text(win + tie / 2, i, f"{tie}%", ha="center", va="center", color="black", fontsize=10)
    ax.text(win + tie + lose / 2, i, f"{lose}%", ha="center", va="center", color="black", fontsize=10)

# Formatting
ax.set_yticks(indices)
ax.set_yticklabels(models)
ax.set_xticks(x_ticks)
ax.set_xticklabels([f"{t}%" for t in x_ticks])  # Add '%' to x-ticks
ax.set_xlim(0, 100)

# Remove unnecessary x-axis label
ax.xaxis.label.set_visible(False)

# Adjust legend styling and position
legend = ax.legend(
    loc='lower center',
    # bbox_to_anchor=(0.5, 1.05),
    # bbox_to_anchor=(0.5, 1.02),
    bbox_to_anchor=(0.25, 1.05),
    ncol=3,
    frameon=False,  # Remove legend box
    title=" ",  # Add space for better alignment
    # fontsize='6',
    handleheight=2.0,  # Increase the height of color boxes
    handlelength=2.5,  # Increase the width of color boxes
    columnspacing=1.50
)
# # Remove borders around legend boxes
# for handle in legend.get_patches():
#     handle.set_edgecolor('none')  # Remove the border around the legend colors
legend.set_title(None)
# Tight layout to avoid clipping
plt.tight_layout()
plt.savefig("winrates.pdf", bbox_inches="tight")
plt.show()
