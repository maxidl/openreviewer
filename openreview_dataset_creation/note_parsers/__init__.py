from .iclr_2021 import parse_iclr_2021_note
from .iclr_2022 import parse_iclr_2022_note
from .iclr_2023 import parse_iclr_2023_note
from .iclr_2024 import parse_iclr_2024_note
from .iclr_2025 import parse_iclr_2025_note
from .neurips_2022 import parse_neurips_2022_note
from .neurips_2023 import parse_neurips_2023_note
from .neurips_2024 import parse_neurips_2024_note

NOTE_PARSERS = {
    "NeurIPS.cc/2024/Conference": parse_neurips_2024_note,
    "NeurIPS.cc/2023/Conference": parse_neurips_2023_note,
    "NeurIPS.cc/2022/Conference": parse_neurips_2022_note,
    # "NeurIPS.cc/2021/Conference": parse_neurips_2021_note,
    "ICLR.cc/2025/Conference": parse_iclr_2025_note,
    "ICLR.cc/2024/Conference": parse_iclr_2024_note,
    "ICLR.cc/2023/Conference": parse_iclr_2023_note,
    "ICLR.cc/2022/Conference": parse_iclr_2022_note,
    "ICLR.cc/2021/Conference": parse_iclr_2021_note,
}


def get_note_parser(venue):
    assert (
        venue in NOTE_PARSERS
    ), f"note parser for venue {venue} does not exists. Available note parsers:\n{list(NOTE_PARSERS.keys())}"
    return NOTE_PARSERS[venue]
