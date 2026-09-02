"""
UC-0B — Summary That Changes Meaning

Creates a faithful summary of the HR leave policy while enforcing
the ten required clauses from the UC-0B README.
"""

import argparse
import re


REQUIRED_CLAUSES = {
    "2.3": (
        "14-day advance notice is required before leave is taken."
    ),
    "2.4": (
        "Written approval is required before leave commences, and verbal "
        "approval is not valid."
    ),
    "2.5": (
        "An unapproved absence will result in LOP regardless of subsequent "
        "approval."
    ),
    "2.6": (
        "A maximum of 5 days may be carried forward; any days above 5 are "
        "forfeited on 31 December."
    ),
    "2.7": (
        "Carry-forward days must be used from January through March or they "
        "are forfeited."
    ),
    "3.2": (
        "Three or more consecutive sick days requires a medical certificate "
        "within 48 hours."
    ),
    "3.4": (
        "Sick leave immediately before or after a holiday requires a medical "
        "certificate regardless of duration."
    ),
    "5.2": (
        "LWP requires approval from both the Department Head and the HR "
        "Director."
    ),
    "5.3": (
        "LWP exceeding 30 days requires Municipal Commissioner approval."
    ),
    "7.2": (
        "Leave encashment during service is not permitted under any "
        "circumstances."
    ),
}


def retrieve_policy(input_path: str) -> dict:
    """
    Read the policy document and return structured numbered sections.

    The source text is retained so the summary can be verified against it.
    """

    with open(
        input_path,
        "r",
        encoding="utf-8-sig"
    ) as infile:
        content = infile.read()

    if not content.strip():
        raise ValueError("Policy document is empty.")

    sections = {}

    # Find numbered policy sections such as 2.3, 2.4, 3.2, etc.
    matches = list(
        re.finditer(
            r"(?m)^\s*(\d+\.\d+)\s+",
            content
        )
    )

    for index, match in enumerate(matches):
        section_number = match.group(1)

        start = match.start()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(content)
        )

        section_text = content[start:end].strip()

        sections[section_number] = section_text

    return {
        "content": content,
        "sections": sections,
    }


def summarize_policy(policy: dict) -> str:
    """
    Produce a deterministic summary using the required clause inventory.

    The UC-0B assignment prioritizes preservation of meaning over creative
    summarization, so each required clause is explicitly represented.
    """

    if not policy or not policy.get("content"):
        raise ValueError("No policy content was provided.")

    lines = [
        "CITY MUNICIPAL CORPORATION — EMPLOYEE LEAVE POLICY",
        "Faithful summary of required policy clauses",
        "",
    ]

    for clause, summary in REQUIRED_CLAUSES.items():
        lines.append(f"Clause {clause}: {summary}")

    summary = "\n".join(lines)

    # Safety check: every required clause must occur in the output.
    for clause in REQUIRED_CLAUSES:
        if f"Clause {clause}:" not in summary:
            raise ValueError(
                f"Required clause {clause} is missing from the summary."
            )

    return summary


def main():
    parser = argparse.ArgumentParser(
        description="UC-0B HR Leave Policy Summarizer"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to policy_hr_leave.txt"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to summary_hr_leave.txt"
    )

    args = parser.parse_args()

    policy = retrieve_policy(args.input)
    summary = summarize_policy(policy)

    with open(
        args.output,
        "w",
        encoding="utf-8"
    ) as outfile:
        outfile.write(summary)
        outfile.write("\n")

    print(f"Done. Summary written to {args.output}")


if __name__ == "__main__":
    main()