import argparse
import time
from pathlib import Path

import polars as pl
import requests
from tqdm.auto import tqdm

OPENREVIEW_URL = "https://openreview.net"


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--notes_df",
        type=str,
        required=True,
        help="parquet file containing notes. must have columns 'id' and 'pdf_url'",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="The output directory.",
    )
    parser.add_argument(
        "--sleep",
        type=float,
        required=False,
        default=2,
        help="The sleep interval between downloads (seconds).",
    )
    return parser.parse_args()


def main(args):
    infile = Path(args.notes_df)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    df = pl.read_parquet(infile).select("id", "pdf_url")

    with tqdm(total=len(df), desc="Downloading pdfs", smoothing=0.9) as pbar:
        for row in df.rows(named=True):
            outfile = output_dir / f"{row['id']}.pdf"
            if outfile.exists():
                pbar.write(f"Skipping {row['id']} : {row['pdf_url']}, already exists.")
                pbar.update()
                continue
            download_url = OPENREVIEW_URL + row["pdf_url"]
            pbar.write(f"Downloading {download_url}")
            try:
                res = requests.get(download_url)
                if res.status_code == 200:
                    pbar.write(f"Saving to {outfile}")
                    pdf_content = res.content
                    with open(outfile, "wb") as f:
                        f.write(pdf_content)
                else:
                    pbar.write(f"Got status code {res.status_code} for url {download_url}.")
                    pbar.write("Waiting 60 secs before proceeding.")
                    time.sleep(60)
            except requests.exceptions.ChunkedEncodingError as e:
                continue
            pbar.update()
            time.sleep(args.sleep)


if __name__ == "__main__":
    args = parse_args()
    print(
        "args:\n" + "\n".join([f"\t{arg}:{value}" for arg, value in vars(args).items()])
    )
    main(args)
