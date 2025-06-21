import json
from typing import Any, Dict

from .data_models import Decision, Note, Review, ParserError


def parse_iclr_2024_note(note: Dict[str, Any]) -> Note:
    def parse_direct_replies(direct_replies):
        reviews = []
        decision = None
        for direct_reply in direct_replies:
            inv = direct_reply["invitations"][0]
            reply_content = direct_reply["content"]
            if "Official_Review" in inv:
                content_fields = [
                    "summary",
                    "soundness",
                    "presentation",
                    "contribution",
                    "strengths",
                    "weaknesses",
                    "questions",
                    "flag_for_ethics_review",
                    "details_of_ethics_concerns",
                    "rating",
                    "confidence",
                ]
                content = [
                    reply_content["summary"]["value"],
                    reply_content["soundness"]["value"],
                    reply_content["presentation"]["value"],
                    reply_content["contribution"]["value"],
                    reply_content["strengths"]["value"],
                    reply_content["weaknesses"]["value"],
                    reply_content["questions"]["value"],
                    "\n".join(reply_content["flag_for_ethics_review"]["value"]),
                    reply_content["details_of_ethics_concerns"]["value"]
                    if "details_of_ethics_concerns" in reply_content
                    else "",
                    reply_content["rating"]["value"],
                    reply_content["confidence"]["value"],
                ]
                content_meta = [
                    "Briefly summarize the paper and its contributions. This is not the place to critique the paper; the authors should generally agree with a well-written summary.",
                    "Please assign the paper a numerical rating on the following scale to indicate the soundness of the technical claims, experimental and research methodology and on whether the central claims of the paper are adequately supported with evidence. Choose from the following:\n4 excellent\n3 good\n2 fair\n1 poor",
                    "Please assign the paper a numerical rating on the following scale to indicate the quality of the presentation. This should take into account the writing style and clarity, as well as contextualization relative to prior work. Choose from the following:\n4 excellent\n3 good\n2 fair\n1 poor",
                    "Please assign the paper a numerical rating on the following scale to indicate the quality of the overall contribution this paper makes to the research area being studied. Are the questions being asked important? Does the paper bring a significant originality of ideas and/or execution? Are the results valuable to share with the broader ICLR community? Choose from the following:\n4 excellent\n3 good\n2 fair\n1 poor",
                    "A substantive assessment of the strengths of the paper, touching on each of the following dimensions: originality, quality, clarity, and significance. We encourage reviewers to be broad in their definitions of originality and significance. For example, originality may arise from a new definition or problem formulation, creative combinations of existing ideas, application to a new domain, or removing limitations from prior results.",
                    "A substantive assessment of the weaknesses of the paper. Focus on constructive and actionable insights on how the work could improve towards its stated goals. Be specific, avoid generic remarks. For example, if you believe the contribution lacks novelty, provide references and an explanation as evidence; if you believe experiments are insufficient, explain why and exactly what is missing, etc.",
                    "Please list up and carefully describe any questions and suggestions for the authors. Think of the things where a response from the author can change your opinion, clarify a confusion or address a limitation. This is important for a productive rebuttal and discussion phase with the authors.",
                    "If there are ethical issues with this paper, please flag the paper for an ethics review and select area of expertise that would be most useful for the ethics reviewer to have. Please select all that apply. Choose from the following:\nNo ethics review needed.\nYes, Discrimination / bias / fairness concerns\nYes, Privacy, security and safety\nYes, Legal compliance (e.g., GDPR, copyright, terms of use)\nYes, Potentially harmful insights, methodologies and applications\nYes, Responsible research practice (e.g., human subjects, data release)\nYes, Research integrity issues (e.g., plagiarism, dual submission)\nYes, Unprofessional behaviors (e.g., unprofessional exchange between authors and reviewers)\nYes, Other reasons (please specify below)",
                    "(Optional) Please provide details of your concerns.",
                    'Please provide an "overall score" for this submission. Choose from the following:\n1: strong reject\n3: reject, not good enough\n5: marginally below the acceptance threshold\n6: marginally above the acceptance threshold\n8: accept, good paper\n10: strong accept, should be highlighted at the conference',
                    'Please provide a "confidence score" for your assessment of this submission to indicate how confident you are in your evaluation. Choose from the following:\n1: You are unable to assess this paper and have alerted the ACs to seek an opinion from different reviewers.\n2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.\n3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.\n4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.\n5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.',
                ]
                review = Review(
                    id=direct_reply["id"],
                    number=direct_reply["number"],
                    forum=direct_reply["forum"],
                    reply_to=direct_reply["replyto"],
                    invitation=direct_reply["invitations"][0],
                    writers=direct_reply["writers"],
                    content=content,
                    content_fields=content_fields,
                    content_meta=content_meta,
                    cdate=direct_reply["cdate"],
                    tcdate=direct_reply["tcdate"],
                    mdate=direct_reply["mdate"],
                    tmdate=direct_reply["tmdate"],
                    ddate=direct_reply["ddate"] if "ddate" in direct_reply else None,
                    tddate=direct_reply["tddate"] if "tddate" in direct_reply else None,
                )
                reviews.append(review)

            elif "Decision" in inv:
                content_fields = ["decision", "comment"]
                content = [
                    reply_content["decision"]["value"],
                    reply_content["comment"]["value"]
                    if "comment" in reply_content
                    else "",
                ]
                content_meta = [
                    "Paper Decision. Choose from the following:\nAccept (oral)\nAccept (spotlight)\nAccept (poster)\nReject\nDecision Pending",
                    "Comment (Optional).",
                ]
                decision = Decision(
                    id=direct_reply["id"],
                    number=direct_reply["number"],
                    forum=direct_reply["forum"],
                    reply_to=direct_reply["replyto"],
                    invitation=direct_reply["invitations"][0],
                    writers=direct_reply["writers"],
                    content=content,
                    content_fields=content_fields,
                    content_meta=content_meta,
                    cdate=direct_reply["cdate"],
                    tcdate=direct_reply["tcdate"],
                    mdate=direct_reply["mdate"],
                    tmdate=direct_reply["tmdate"],
                    ddate=direct_reply["ddate"] if "ddate" in direct_reply else None,
                    tddate=direct_reply["tddate"] if "tddate" in direct_reply else None,
                )
        return reviews, decision

    details = note["details"]
    content = note["content"]
    reviews, decision = parse_direct_replies(details["directReplies"])
    if not reviews:  # or decision is None:
        raise ParserError(f"Found no reviews in note. forum: {note['forum']}")

    return Note(
        id=note["id"],
        number=note["number"],
        forum=note["forum"],
        or_venue=note["or_venue"],
        venue=content["venue"]["value"],
        venueid=content["venueid"]["value"],
        title=content["title"]["value"],
        authors=content["authors"]["value"],
        author_ids=content["authorids"]["value"],
        keywords=content["keywords"]["value"],
        summary=content["TLDR"]["value"] if "TLDR" in content else "",
        abstract=content["abstract"]["value"],
        area=content["primary_area"]["value"],
        paperhash=content["paperhash"]["value"],
        bibtex=content["_bibtex"]["value"],
        pdf_url=content["pdf"]["value"],
        original_pdf_url=None,
        supplementary_material_url=content["supplementary_material"]["value"]
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
