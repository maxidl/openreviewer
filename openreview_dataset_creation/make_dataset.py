import argparse

from pathlib import Path
import polars as pl
from tqdm.auto import tqdm


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--notes_dir",
        type=Path,
        required=True,
        help="directory containing parsed notes",
    )
    parser.add_argument(
        "--pdf_md_dir",
        type=Path,
        required=True,
        help="directory containing pdf md files",
    )
    parser.add_argument(
        "--output_dir",
        type=Path,
        required=True,
        help="The output directory.",
    )
    return parser.parse_args()


def read_notes(notes_dir: Path) -> pl.DataFrame:
    dfs = []
    for file in sorted(list(notes_dir.glob("**/*.parquet"))):
        print(f"reading file: {file}")
        df = pl.read_parquet(file)
        print(df.shape)
        dfs.append(df)
    return pl.concat(dfs, how="vertical_relaxed")


def load_text(note_id, pdf_md_dir: Path):
    md_file = pdf_md_dir / note_id / f"{note_id}.md"
    with open(md_file, "r") as f:
        content = f.read()
    return content


def main(args):
    # args = argparse.Namespace()
    # args.notes_dir = Path("data/notes_parsed")
    # args.pdf_md_dir = Path("data/pdfs_marker")
    # args.output_dir = Path("data/dataset/v1")

    args.output_dir.mkdir(exist_ok=True, parents=True)


    outfile = args.output_dir / "notes.zstd.parquet"
    if outfile.exists():
        raise FileExistsError(f"output file {outfile.absolute()} already exists.")

    df = read_notes(args.notes_dir)
    print(df.shape)

    # add text
    texts = []
    for row in tqdm(df.select(pl.col("id")).rows(named=True), desc="loading md text"):
        text = load_text(row["id"], args.pdf_md_dir)
        texts.append(text)
    df = df.with_columns(pl.Series(name="pdf_md", values=texts))
    
    # add some useful columns    # add some useful columns
    df = df.with_columns(num_reviews=pl.col("reviews").list.len())
    df = df.with_columns(pdf_md_num_chars=pl.col("pdf_md").str.len_chars())
    # df = df.with_columns(pdf_md_main_text_num_chars=pl.col("pdf_md_main_text").str.len_chars())
    # df = df.with_columns(pdf_md_appendix_text_num_chars=pl.col("pdf_md_appendix_text").str.len_chars())
    

    df.write_parquet(outfile)

if __name__ == "__main__":
    args = parse_args()
    print(
        "args:\n" + "\n".join([f"\t{arg}:{value}" for arg, value in vars(args).items()])
    )
    main(args)
