import argparse
import pickle
from pathlib import Path

import polars as pl
from note_parsers import get_note_parser
from note_parsers.data_models import ParserError


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--notes",
        type=str,
        required=True,
        help="pkl file containing notes",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="The output directory.",
    )
    return parser.parse_args()


def main(args):

    infile = Path(args.notes)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    outfile = Path(args.output_dir) / f"{infile.stem}.zstd.parquet"
    if outfile.exists():
        raise FileExistsError(f"output file {outfile.absolute()} already exists.")

    with open(infile, "rb") as f:
        notes = pickle.load(f)
    print(f"Notes: {len(notes):_}")

    parsed_notes = []
    for note in notes:
        parse_fn = get_note_parser(note["or_venue"])
        try:
            parsed_note = parse_fn(note).model_dump()
            parsed_notes.append(parsed_note)
        except ParserError as e:
            print(e)

    df = pl.from_dicts(parsed_notes)
    df.write_parquet(outfile)
    print(df.shape)


if __name__ == "__main__":
    args = parse_args()
    print(
        "args:\n" + "\n".join([f"\t{arg}:{value}" for arg, value in vars(args).items()])
    )
    main(args)
