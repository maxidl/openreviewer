import argparse
from pathlib import Path
import polars as pl
import matplotlib.pyplot as plt


pl.Config.set_tbl_rows(100)



def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="The dataset to compute statistics for.",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="The output directory.",
    )
    return parser.parse_args()


def main(args):

    args.output_dir.mkdir(exist_ok=True, parents=True)

    with open(args.output_dir / "statistics.txt", "w") as f:

        df = pl.read_parquet(args.dataset)

        number_of_papers = df.shape[0]
        print(f"Number of papers: {number_of_papers}", file=f)

        # decisions
        count_dfs = []
        for df_by_venue in df.partition_by('or_venue'):
            print(f"Venue:{df_by_venue.select('or_venue').unique().item()}", file=f)
            decision_index = df_by_venue.select(pl.col("decision").struct.field("content_fields").list.eval((pl.element() == 'decision').cast(int)).list.arg_max().mode()).item()
            decision_counts = df_by_venue.select(pl.col("decision").struct.field("content").list.get(decision_index).value_counts()).unnest('content').sort('count', descending=True).rename({'content': 'decision'})
            print(f"Decisions: {decision_counts}", file=f)
            count_dfs.append(decision_counts)

        count_df = pl.concat(count_dfs)
        count_df = count_df.group_by('decision').sum().sort('count', descending=True)
        print(f"Total decisions: {count_df}", file=f)

        # paper text
        md_lengths = df.select(pl.col('pdf_md').str.len_chars())
        print(md_lengths.describe(percentiles=(.25, .5, .75, .99)), file=f)
        fig = md_lengths.to_pandas().plot.hist(bins=100)
        fig.set_xlabel("Paper length (chars)")
        fig.set_ylabel("Number of papers")
        plt.tight_layout()
        plt.savefig(args.output_dir / "paper_lengths.png")
        
        # reviews
        print(df.select(pl.col('num_reviews')).describe(), file=f)
        fig = df.select(pl.col('num_reviews').value_counts()).unnest('num_reviews').sort('num_reviews').to_pandas().plot.bar(x='num_reviews', y='count', figsize=(10, 6))
        fig.set_xlabel("Number of reviews")
        fig.set_ylabel("Number of papers")
        plt.tight_layout()
        plt.savefig(args.output_dir / "num_reviews_per_paper.png")

        
        df = df.explode('reviews')
        df = df.rename({'reviews': 'review'})
        print(f"Number of reviews: {df.shape[0]}", file=f)
        review_lengths = df.select(pl.col('review').struct.field('content').list.join('\n').str.len_chars())
        print(review_lengths.describe(percentiles=(.25, .5, .75, .99)), file=f)
        fig = review_lengths.to_pandas().plot.hist(bins=100)
        fig.set_xlabel("Review length (chars)")
        fig.set_ylabel("Number of reviews")
        plt.tight_layout()
        plt.savefig(args.output_dir / "review_lengths.png")









if __name__ == "__main__":
    args = parse_args()
    print(
        "args:\n" + "\n".join([f"\t{arg}:{value}" for arg, value in vars(args).items()])
    )
    main(args)


