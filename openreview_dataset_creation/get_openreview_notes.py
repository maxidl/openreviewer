import argparse
import json
import pickle
from pathlib import Path
import os

from openreview_utils import get_client


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--or_venue",
        type=str,
        required=True,
        help="The venue to get notes for, e.g. 'ICLR.cc/2022/Conference'",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="The output directory.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        required=False,
        help="Force getting notes even if file exists.",
    )
    return parser.parse_args()


def main(args):
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    outfile = Path(args.output_dir) / f"{args.or_venue.replace('/', '_')}.pkl"
    if outfile.exists():
        if not args.force:
            raise FileExistsError(f"output file {outfile.absolute()} already exists.")

    notes = dict()
    # Following https://docs.openreview.net/how-to-guides/data-retrieval-and-modification/how-to-get-all-reviews
    # v2
    api_v2 = True
    print("trying API V2")
    or_username = os.environ.get('OPENREVIEW_USERNAME')
    or_password = os.environ.get('OPENREVIEW_PASSWORD')
    if not or_username or not or_password:
        raise ValueError("OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD must be set as environment variables")
    client = get_client(
        version=2, or_username=or_username, or_password=or_password
    )
    venue_group = client.get_group(args.or_venue)
    if venue_group.content:
        submission_name = venue_group.content["submission_name"]["value"]
        notes = client.get_all_notes(
            invitation=f"{args.or_venue}/-/{submission_name}", details="all"
        )
        notes = {note.id: note for note in notes}
    else:
        "failed to get information from API V2"
    if not notes:
        print("could not find any notes.")
        print("switching to V1 API and trying again")
        # v1
        api_v2 = False
        print("trying API V1")
        client = get_client(
            version=1, or_username=or_username, or_password=or_password
        )
        print("trying to find notes by invitation: /-/Blind_Submission")
        notes_doubleblind = client.get_all_notes(
            invitation=f"{args.or_venue}/-/Blind_Submission", details="all"
        )
        notes_doubleblind = {note.id: note for note in notes_doubleblind}
        print(f"\tgot {len(notes_doubleblind)} notes")
        notes.update(notes_doubleblind)
        print("trying to find notes by invitation: /-/Submission")
        notes_singleblind = client.get_all_notes(
            invitation=f"{args.or_venue}/-/Submission", details="all"
        )
        notes_singleblind = {note.id: note for note in notes_singleblind}
        print(f"\tgot {len(notes_singleblind)} notes")
        notes.update(notes_singleblind)

    print(f"Got {len(notes):_} unique notes.")
    if not notes:
        raise ValueError(
            f"No notes to process. Did you provide a correct venue?\n{args.or_venue}"
        )

    rows = []
    for note in notes.values():
        note_dict = note.__dict__
        note_dict["or_venue"] = args.or_venue
        rows.append(note_dict)

    print(f"writing notes to {outfile.absolute()}")
    with open(outfile, "wb") as f:
        pickle.dump(rows, f)

    # get reply templates
    if api_v2:
        invitations = [
            reply["invitations"][0]
            for note in rows
            for reply in note["details"]["replies"]
        ]
    else:
        invitations = [
            reply["invitation"] for note in rows for reply in note["details"]["replies"]
        ]
    invitation_types = sorted(list(set([inv.split("/")[-1] for inv in invitations])))
    selected_invs = []
    for invitation_type in invitation_types:
        for inv in invitations:
            if invitation_type in inv:
                selected_invs.append(inv)
                break
    selected_invs = [
        client.get_invitations(id=inv, expired=True)[0].__dict__
        for inv in selected_invs
    ]

    # get submission template
    submission_template = rows[0]["details"]["invitation"]

    outfile = outfile.parent / f"{outfile.stem}.template.json"
    print(f"writing templates to {outfile.absolute()}")
    with open(outfile, "w") as f:
        json.dump(
            {
                "submission_template": submission_template,
                "reply_templates": selected_invs,
            },
            f,
        )


if __name__ == "__main__":
    args = parse_args()
    print(
        "args:\n" + "\n".join([f"\t{arg}:{value}" for arg, value in vars(args).items()])
    )
    main(args)
