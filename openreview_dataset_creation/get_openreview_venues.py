import argparse
from pathlib import Path
import openreview
import os

from openreview_utils import get_client


def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="The output directory.",
    )
    return parser.parse_args()


def main(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    or_username = os.environ.get('OPENREVIEW_USERNAME')
    or_password = os.environ.get('OPENREVIEW_PASSWORD')
    if not or_username or not or_password:
        raise ValueError("OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD must be set as environment variables")

    client = get_client(
        version=2, or_username=or_username, or_password=or_password
    )
    
    venues_group = client.get_group(id="venues")
    venues = sorted(venues_group.members)
    
    print(f"Got {len(venues):_} venues.")
    
    output_file = output_dir / "or_venues.txt"
    print(f"Saving to {output_file}")
    
    with open(output_file, "w") as f:
        f.write("\n".join(venues) + "\n")


if __name__ == "__main__":
    args = parse_args()
    main(args)
