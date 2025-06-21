import json
from typing import Any, Dict

from .data_models import Decision, Note, Review


def parse_iclr_2021_note(note: Dict[str, Any]) -> Note:
    def parse_direct_replies(direct_replies):
        reviews = []
        decision = None
        for direct_reply in direct_replies:
            inv = direct_reply["invitation"]
            reply_content = direct_reply["content"]
            if "Official_Review" in inv:
                content_fields = [
                    "review_summary",
                    "review",
                    "rating",
                    "confidence",
                ]
                content = [
                    reply_content["title"],
                    reply_content["review"],
                    reply_content["rating"],
                    reply_content["confidence"],
                ]
                content_meta = [
                    "Brief summary of your review (max 500 characters).",
                    "Please provide an evaluation of the quality, clarity, originality and significance of this work, including a list of its pros and cons (max 200000 characters).",
                    "Your rating. Choose from the following:\n10: Top 5% of accepted papers, seminal paper\n9: Top 15% of accepted papers, strong accept\n8: Top 50% of accepted papers, clear accept\n7: Good paper, accept\n6: Marginally above acceptance threshold\n5: Marginally below acceptance threshold\n4: Ok but not good enough - rejection\n3: Clear rejection\n2: Strong rejection\n1: Trivial or wrong",
                    "Your confidence. Choose from the following:\n5: The reviewer is absolutely certain that the evaluation is correct and very familiar with the relevant literature\n4: The reviewer is confident but not absolutely certain that the evaluation is correct\n3: The reviewer is fairly confident that the evaluation is correct\n2: The reviewer is willing to defend the evaluation, but it is quite likely that the reviewer did not understand central parts of the paper\n1: The reviewer's evaluation is an educated guess",
                ]
                review = Review(
                    id=direct_reply["id"],
                    number=direct_reply["number"],
                    forum=direct_reply["forum"],
                    reply_to=direct_reply["replyto"],
                    invitation=direct_reply["invitation"],
                    writers=direct_reply["writers"],
                    content=content,
                    content_fields=content_fields,
                    content_meta=content_meta,
                    cdate=direct_reply["cdate"],
                    tcdate=direct_reply["tcdate"],
                    mdate=direct_reply["mdate"] if "mdate" in direct_reply else None,
                    tmdate=direct_reply["tmdate"],
                    ddate=direct_reply["ddate"],
                    tddate=direct_reply["tddate"],
                )
                reviews.append(review)

            elif "Decision" in inv:
                content_fields = ["decision", "comment"]
                content = [
                    reply_content["decision"],
                    reply_content["comment"],
                ]

                content_meta = [
                    "Final Decision. Choose from the following:\nAccept (Oral)\nAccept (Spotlight)\nAccept (Poster)\nReject",
                    "Comment (Optional).",
                ]

                decision = Decision(
                    id=direct_reply["id"],
                    number=direct_reply["number"],
                    forum=direct_reply["forum"],
                    reply_to=direct_reply["replyto"],
                    invitation=direct_reply["invitation"],
                    writers=direct_reply["writers"],
                    content=content,
                    content_fields=content_fields,
                    content_meta=content_meta,
                    cdate=direct_reply["cdate"],
                    tcdate=direct_reply["tcdate"],
                    mdate=direct_reply["mdate"] if "mdate" in direct_reply else None,
                    tmdate=direct_reply["tmdate"],
                    ddate=direct_reply["ddate"],
                    tddate=direct_reply["tddate"],
                )
        return reviews, decision

    details = note["details"]
    content = note["content"]
    reviews, decision = parse_direct_replies(details["directReplies"])

    return Note(
        id=note["id"],
        number=note["number"],
        forum=note["forum"],
        or_venue=note["or_venue"],
        venue=content["venue"] if "venue" in content else None,
        venueid=content["venueid"] if "venueid" in content else None,
        title=content["title"],
        authors=content["authors"],
        author_ids=content["authorids"],
        keywords=content["keywords"],
        summary=content["one-sentence_summary"]
        if "one-sentence_summary" in content
        else None,
        abstract=content["abstract"],
        area=None,
        paperhash=content["paperhash"],
        bibtex=content["_bibtex"],
        pdf_url=content["pdf"],
        original_pdf_url=None,
        supplementary_material_url=content["supplementary_material"]
        if "supplementary_material" in content
        else None,
        code=None,
        data=None,
        cdate=note["cdate"],
        tcdate=note["tcdate"],
        mdate=note["mdate"],
        tmdate=note["tmdate"],
        pdate=note["pdate"],
        odate=note["odate"],
        ddate=note["ddate"],
        tags=details["tags"],
        reply_count=details["replyCount"],
        direct_reply_count=details["directReplyCount"],
        replies=json.dumps(details["replies"]),
        direct_replies=json.dumps(details["directReplies"]),
        reviews=reviews,
        decision=decision,
    )
