import json
from typing import Any, Dict

from .data_models import Decision, Note, Review


def parse_neurips_2023_note(note: Dict[str, Any]) -> Note:
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
                    "limitations",
                    "flag_for_ethics_review",
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
                    reply_content["limitations"]["value"],
                    "\n".join(reply_content["flag_for_ethics_review"]["value"]),
                    reply_content["rating"]["value"],
                    reply_content["confidence"]["value"],
                ]
                content_meta = [
                    "Briefly summarize the paper and its contributions. This is not the place to critique the paper; the authors should generally agree with a well-written summary.",
                    "Please assign the paper a numerical rating on the following scale to indicate the soundness of the technical claims, experimental and research methodology and on whether the central claims of the paper are adequately supported with evidence.\n4 excellent\n3 good\n2 fair\n1 poor",
                    "Please assign the paper a numerical rating on the following scale to indicate the quality of the presentation. This should take into account the writing style and clarity, as well as contextualization relative to prior work.\n4 excellent\n3 good\n2 fair\n1 poor",
                    "Please assign the paper a numerical rating on the following scale to indicate the quality of the overall contribution this paper makes to the research area being studied. Are the questions being asked important? Does the paper bring a significant originality of ideas and/or execution? Are the results valuable to share with the broader NeurIPS community?\n4 excellent\n3 good\n2 fair\n1 poor",
                    "A substantive assessment of the strengths of the paper, touching on each of the following dimensions: originality, quality, clarity, and significance. We encourage reviewers to be broad in their definitions of originality and significance. For example, originality may arise from a new definition or problem formulation, creative combinations of existing ideas, application to a new domain, or removing limitations from prior results.",
                    "A substantive assessment of the weaknesses of the paper. Focus on constructive and actionable insights on how the work could improve towards its stated goals. Be specific, avoid generic remarks. For example, if you believe the contribution lacks novelty, provide references and an explanation as evidence; if you believe experiments are insufficient, explain why and exactly what is missing, etc.",
                    "Please list up and carefully describe any questions and suggestions for the authors. Think of the things where a response from the author can change your opinion, clarify a confusion or address a limitation. This is important for a productive rebuttal and discussion phase with the authors.",
                    "Have the authors adequately addressed the limitations and, if applicable, potential negative societal impact of their work? If not, please include constructive suggestions for improvement. Authors should be rewarded rather than punished for being up front about the limitations of their work and any potential negative societal impact.",
                    "If there are ethical issues with this paper, please flag the paper for an ethics review and select area of expertise that would be most useful for the ethics reviewer to have. Please select all that apply. \nNo ethics review needed.\nEthics review needed: Discrimination / Bias / Fairness Concerns\nEthics review needed: Inadequate Data and Algorithm Evaluation\nEthics review needed: Inappropriate Potential Applications & Impact  (e.g., human rights concerns)\nEthics review needed: Privacy and Security (e.g., consent, surveillance, data storage concern)\nEthics review needed: Compliance (e.g., GDPR, copyright, license, terms of use)\nEthics review needed: Research Integrity Issues (e.g., plagiarism)\nEthics review needed: Responsible Research Practice (e.g., IRB, documentation, research ethics)\nEthics review needed: Failure to comply with NeurIPS Code of Ethics (lack of required documentation, safeguards, disclosure, licenses, legal compliance)",
                    'Please provide an "overall score" for this submission. Choose from the following:\n10: Award quality: Technically flawless paper with groundbreaking impact, with exceptionally strong evaluation, reproducibility, and resources, and no unaddressed ethical considerations.\n9: Very Strong Accept: Technically flawless paper with groundbreaking impact on at least one area of AI/ML and excellent impact on multiple areas of AI/ML, with flawless evaluation, resources, and reproducibility, and no unaddressed ethical considerations.\n8: Strong Accept: Technically strong paper, with novel ideas, excellent impact on at least one area, or high-to-excellent impact on multiple areas, with excellent evaluation, resources, and reproducibility, and no unaddressed ethical considerations.\n7: Accept: Technically solid paper, with high impact on at least one sub-area, or moderate-to-high impact on more than one areas, with good-to-excellent evaluation, resources, reproducibility, and no unaddressed ethical considerations.\n6: Weak Accept: Technically solid, moderate-to-high impact paper, with no major concerns with respect to evaluation, resources, reproducibility, ethical considerations.\n5: Borderline accept: Technically solid paper where reasons to accept outweigh reasons to reject, e.g., limited evaluation. Please use sparingly.\n4: Borderline reject: Technically solid paper where reasons to reject, e.g., limited evaluation, outweigh reasons to accept, e.g., good evaluation. Please use sparingly.\n3: Reject: For instance, a paper with technical flaws, weak evaluation, inadequate reproducibility and incompletely addressed ethical considerations.\n2: Strong Reject: For instance, a paper with major technical flaws, and/or poor evaluation, limited impact, poor reproducibility and mostly unaddressed ethical considerations.\n1: Very Strong Reject: For instance, a paper with trivial results or unaddressed ethical considerations.',
                    'Please provide a "confidence score" for your assessment of this submission to indicate how confident you are in your evaluation. Choose from the following:\n5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully.\n4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work.\n3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.\n2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked.\n1: Your assessment is an educated guess. The submission is not in your area or the submission was difficult to understand. Math/other details were not carefully checked.',
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
                    ddate=None,
                    tddate=None,
                )
                reviews.append(review)

            elif "Decision" in inv:
                content_fields = ["decision", "comment"]
                content = [
                    reply_content["decision"]["value"],
                    reply_content["comment"]["value"],
                ]
                content_meta = [
                    "Paper Decision. Choose from the following:\nAccept (oral)\nAccept (spotlight)\nAccept (poster)\nReject",
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
                    ddate=None,
                    tddate=None,
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
        venue=content["venue"]["value"],
        venueid=content["venueid"]["value"],
        title=content["title"]["value"],
        authors=content["authors"]["value"],
        author_ids=content["authorids"]["value"],
        keywords=content["keywords"]["value"],
        summary=content["TLDR"]["value"] if "TLDR" in content else None,
        abstract=content["abstract"]["value"],
        area=None,
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
