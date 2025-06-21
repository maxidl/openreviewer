import json
from typing import Any, Dict

from .data_models import Decision, Note, Review


def parse_iclr_2023_note(note: Dict[str, Any]) -> Note:
    def parse_direct_replies(direct_replies):
        reviews = []
        decision = None
        for direct_reply in direct_replies:
            inv = direct_reply["invitation"]
            reply_content = direct_reply["content"]
            if "Review" in inv:
                content_fields = [
                    "summary_of_the_paper",
                    "strength_and_weaknesses",
                    "clarity,_quality,_novelty_and_reproducibility",
                    "summary_of_the_review",
                    "correctness",
                    "technical_novelty_and_significance",
                    "empirical_novelty_and_significance",
                    "flag_for_ethics_review",
                    "details_of_ethics_concerns",
                    "recommendation",
                    "confidence",
                ]
                content = [
                    reply_content["summary_of_the_paper"],
                    reply_content["strength_and_weaknesses"],
                    reply_content["clarity,_quality,_novelty_and_reproducibility"],
                    reply_content["summary_of_the_review"],
                    reply_content["correctness"],
                    reply_content["technical_novelty_and_significance"],
                    reply_content["empirical_novelty_and_significance"],
                    "\n".join(reply_content["flag_for_ethics_review"]),
                    reply_content["details_of_ethics_concerns"]
                    if "details_of_ethics_concerns" in reply_content
                    else "",
                    reply_content["recommendation"],
                    reply_content["confidence"],
                ]
                content_meta = [
                    "Provide a brief summary of the paper and its contributions.",
                    "Please list both the strengths and weaknesses of the paper. When discussing weaknesses, please provide concrete, actionable feedback on the paper.",
                    "Can you provide an evaluation of the quality, clarity and originality of the work?",
                    "Please provide a short summary justifying your recommendation of the paper.",
                    "When evaluating correctness, we urge reviewers to focus on the technical content of the paper instead of language. This is especially important to support researchers from diverse geographical backgrounds. Choose from the following:\n1: The main claims of the paper are incorrect or not at all supported by theory or empirical results.\n2: Several of the paper\u2019s claims are incorrect or not well-supported.\n3: Some of the paper\u2019s claims have minor issues. A few statements are not well-supported, or require small changes to be made correct.\n4: All of the claims and statements are well-supported and correct.",
                    "For this question, contributions are technical in nature, including new models, techniques, or theoretical insights. Choose from the following:\n1: The contributions are neither significant nor novel.\n2: The contributions are only marginally significant or novel.\n3: The contributions are significant and somewhat new. Aspects of the contributions exist in prior work.\n4: The contributions are significant, and do not exist in prior works.",
                    "For this question, contributions include new insights supported by empirical results including those arising from new benchmarks or datasets. Choose from the following:\nNot applicable\n1: The contributions are neither significant nor novel.\n2: The contributions are only marginally significant or novel.\n3: The contributions are significant and somewhat new. Aspects of the contributions exist in prior work.\n4: The contributions are significant, and do not exist in prior works.",
                    "Choose one or more from the following entries:\nNO.\nYes, Discrimination / bias / fairness concerns\nYes, Privacy, security and safety\nYes, Legal compliance (e.g., GDPR, copyright, terms of use)\nYes, Potentially harmful insights, methodologies and applications\nYes, Responsible research practice (e.g., human subjects, data release)\nYes, Research integrity issues (e.g., plagiarism, dual submission)\nYes, Unprofessional behaviors (e.g., unprofessional exchange between authors and reviewers)\nYes, Other reasons (please specify below)",
                    "Please provide details of your concerns.",
                    "Your recommendation. Choose from the following:\n1: strong reject\n3: reject, not good enough\n5: marginally below the acceptance threshold\n6: marginally above the acceptance threshold\n8: accept, good paper\n10: strong accept, should be highlighted at the conference",
                    "Your confidence. Choose from the following:\n1: You are unable to assess this paper and have alerted the ACs to seek an opinion from different reviewers.\n2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.\n3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.\n4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.\n5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.",
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
                    mdate=direct_reply["mdate"],
                    tmdate=direct_reply["tmdate"],
                    ddate=direct_reply["ddate"],
                    tddate=direct_reply["tddate"],
                )
                reviews.append(review)

            elif "Decision" in inv:
                content_fields = [
                    "decision",
                    "comment",
                    "metareview:_summary,_strengths_and_weaknesses",
                    "summary_of_AC-reviewer_meeting",
                    "justification_for_why_not_higher_score",
                    "justification_for_why_not_lower_score",
                ]
                content = [
                    reply_content["decision"],
                    reply_content["comment"] if "comment" in reply_content else "",
                    reply_content["metareview:_summary,_strengths_and_weaknesses"],
                    reply_content["summary_of_AC-reviewer_meeting"]
                    if "summary_of_AC-reviewer_meeting" in reply_content
                    else "",
                    reply_content["justification_for_why_not_higher_score"],
                    reply_content["justification_for_why_not_lower_score"],
                ]
                content_meta = [
                    "Paper Decision. Choose from the following:\nAccept: notable-top-5%\nAccept: notable-top-25%\nAccept: poster\nReject\nConditional Accept",
                    "Comment (Optional).",
                    "Please fill out the following section (max 5000 characters): (a) Summarize the scientific claims and findings of the paper based on your own reading and characterizations from the reviewers. (b) What are the strengths of the paper? (c) What are the weaknesses of the paper? What might be missing in the submission?",
                    "If this was a borderline paper, please summarize the meeting with reviewers. What were the points raised by the reviewers? How were each of these points addressed by the authors? How did you weigh in each point in your final decision?",
                    "Please state the reasons behind the current recommendation, especially why not a higher score (e.g., if you choose Accept with spotlight, why not Accept with oral). If your recommendation is already the highest score (Accept with Oral), then put N/A. Your justification should be based on what you articulated in the above points of part 1 and 2.",
                    "Please state the reasons behind the current recommendation, especially why not a lower score (e.g., if you choose Accept with poster, why not reject). If your recommendation is already the lowest score (Reject), then please put N/A.",
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
                    mdate=direct_reply["mdate"],
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
        venue=content["venue"],
        venueid=content["venueid"],
        title=content["title"],
        authors=content["authors"],
        author_ids=content["authorids"],
        keywords=content["keywords"],
        summary=content["TL;DR"] if "TL;DR" in content else None,
        abstract=content["abstract"],
        area=content["Please_choose_the_closest_area_that_your_submission_falls_into"]
        if "Please_choose_the_closest_area_that_your_submission_falls_into" in content
        else None,
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
