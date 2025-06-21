import json
from typing import Any, Dict, Sequence, Optional

from pydantic import BaseModel, ValidationInfo, field_validator


class ParserError(Exception):
    pass


class Decision(BaseModel):
    id: str
    number: int
    forum: str
    reply_to: str
    invitation: str
    writers: Sequence[str]

    # content fields
    content_fields: Sequence[str]
    content: Sequence[str]
    content_meta: Sequence[str]

    # time fields
    cdate: Optional[int] = None
    tcdate: Optional[int] = None
    mdate: Optional[int] = None
    tmdate: Optional[int] = None
    ddate: Optional[int] = None
    tddate: Optional[int] = None


class Review(BaseModel):
    id: str
    number: int
    forum: str
    reply_to: str
    invitation: str
    writers: Sequence[str]

    # content fields
    content_fields: Sequence[str]
    content: Sequence[str]
    content_meta: Sequence[str]

    # time fields
    cdate: Optional[int] = None
    tcdate: Optional[int] = None
    mdate: Optional[int] = None
    tmdate: Optional[int] = None
    ddate: Optional[int] = None
    tddate: Optional[int] = None


class Note(BaseModel):
    id: str
    number: int
    forum: str
    or_venue: str

    # content fields
    venue: Optional[str]
    venueid: Optional[str]
    title: str
    authors: Optional[Sequence[str]]
    author_ids: Optional[Sequence[str]]
    keywords: Sequence[str]
    summary: Optional[str]
    abstract: str
    area: Optional[str]
    paperhash: Optional[str]
    bibtex: str
    pdf_url: str
    original_pdf_url: Optional[str]
    supplementary_material_url: Optional[str]
    code: Optional[Sequence[str]]
    data: Optional[Sequence[str]]

    # time fields
    cdate: Optional[int] = None
    tcdate: Optional[int] = None
    mdate: Optional[int] = None
    tmdate: Optional[int] = None
    pdate: Optional[int] = None
    odate: Optional[int] = None
    ddate: Optional[int] = None

    # details fields
    tags: Optional[Sequence["str"]]
    reply_count: int
    direct_reply_count: int
    replies: str
    direct_replies: str

    # parsed details
    reviews: Sequence[Review]
    decision: Optional[Decision]  # make optional since withdrawn papers often have reviews but no decision.

    @field_validator("replies", "direct_replies")
    @classmethod
    def check_valid_json(cls, s: str, info: ValidationInfo) -> str:
        assert json.loads(s)
        return s
