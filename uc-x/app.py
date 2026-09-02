"""
UC-X - Ask My Documents

Conservative policy question answering system.

Rules:
- Load all three supplied policy documents.
- Answer from one source document only.
- Cite the exact document and section.
- Never combine claims from different documents.
- Refuse when the question cannot be answered confidently.
"""

import argparse
import re
from pathlib import Path


DOCUMENTS = [
    "policy_hr_leave.txt",
    "policy_it_acceptable_use.txt",
    "policy_finance_reimbursement.txt",
]

REFUSAL = (
    "This question is not covered in the available policy documents "
    "(policy_hr_leave.txt, policy_it_acceptable_use.txt, "
    "policy_finance_reimbursement.txt). "
    "Please contact [relevant team] for guidance."
)


# Explicit question concepts mapped to the section that governs them.
# These are routing hints, not new policy claims.
KNOWN_ROUTES = {
    # HR
    "carry forward unused annual leave": ("policy_hr_leave.txt", "2.6"),
    "carry forward annual leave": ("policy_hr_leave.txt", "2.6"),
    "unused annual leave": ("policy_hr_leave.txt", "2.6"),
    "leave without pay": ("policy_hr_leave.txt", "5.2"),
    "lwp": ("policy_hr_leave.txt", "5.2"),

    # IT
    "install slack": ("policy_it_acceptable_use.txt", "2.3"),
    "slack": ("policy_it_acceptable_use.txt", "2.3"),
    "install software": ("policy_it_acceptable_use.txt", "2.3"),
    "software on work laptop": ("policy_it_acceptable_use.txt", "2.3"),

    # Finance
    "home office equipment allowance": (
        "policy_finance_reimbursement.txt",
        "3.1",
    ),
    "equipment allowance": (
        "policy_finance_reimbursement.txt",
        "3.1",
    ),
    "da and meal": (
        "policy_finance_reimbursement.txt",
        "2.6",
    ),
    "meal receipts": (
        "policy_finance_reimbursement.txt",
        "2.6",
    ),
    "claim da": (
        "policy_finance_reimbursement.txt",
        "2.6",
    ),
}


def parse_sections(text):
    """
    Extract numbered sections without allowing decorative headings
    to become part of the previous section.

    A section starts at a line containing a number such as 2.3.
    """
    lines = text.splitlines()

    sections = {}
    current_number = None
    current_lines = []

    section_pattern = re.compile(r"^\s*(\d+\.\d+)\s+(.*)$")

    for line in lines:
        match = section_pattern.match(line)

        if match:
            if current_number is not None:
                body = " ".join(current_lines).strip()
                body = re.sub(r"\s+", " ", body)
                if body:
                    sections[current_number] = body

            current_number = match.group(1)
            current_lines = [match.group(2)]
        elif current_number is not None:
            # Ignore obvious decorative separator lines.
            stripped = line.strip()

            if stripped and not re.fullmatch(r"[^A-Za-z0-9]+", stripped):
                current_lines.append(stripped)

    if current_number is not None:
        body = " ".join(current_lines).strip()
        body = re.sub(r"\s+", " ", body)

        if body:
            sections[current_number] = body

    return sections


def retrieve_documents(policy_dir):
    """Load and index all three policy documents."""
    policy_dir = Path(policy_dir)
    indexed = {}

    for filename in DOCUMENTS:
        path = policy_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required policy document not found: {path}"
            )

        text = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        sections = parse_sections(text)

        if not sections:
            raise ValueError(
                f"No numbered policy sections found in {filename}"
            )

        indexed[filename] = sections

    return indexed


def normalize(text):
    """Normalize text for comparison."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_known_route(question):
    """
    Route clearly recognizable questions to the governing section.

    This prevents common wording differences from causing false
    refusals while keeping the answer tied to one source.
    """
    q = normalize(question)

    # Longest phrases first.
    for phrase, route in sorted(
        KNOWN_ROUTES.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if phrase in q:
            return route

    return None


def question_terms(question):
    """Extract meaningful terms from the question."""
    stop_words = {
        "can", "could", "may", "might", "should", "would",
        "what", "when", "where", "who", "how", "why",
        "is", "are", "do", "does", "did",
        "i", "me", "my", "we", "our", "you", "your",
        "the", "a", "an", "to", "of", "for", "and", "or",
        "on", "in", "at", "from", "with",
        "please", "tell", "about",
    }

    return {
        word
        for word in normalize(question).split()
        if len(word) > 2 and word not in stop_words
    }


def score_section(question, section_text):
    """Calculate conservative lexical evidence."""
    q_terms = question_terms(question)
    section_terms = set(normalize(section_text).split())

    return len(q_terms & section_terms)


def find_best_source(question, indexed):
    """
    Find one strong source.

    Known routes take priority. Otherwise use lexical matching,
    but never merge documents.
    """
    route = find_known_route(question)

    if route:
        filename, section_number = route

        if (
            filename in indexed
            and section_number in indexed[filename]
        ):
            return (
                100,
                filename,
                section_number,
                indexed[filename][section_number],
            )

    candidates = []

    for filename, sections in indexed.items():
        for section_number, section_text in sections.items():
            score = score_section(question, section_text)

            if score >= 2:
                candidates.append(
                    (
                        score,
                        filename,
                        section_number,
                        section_text,
                    )
                )

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    best = candidates[0]

    # If different documents have equal evidence, refuse rather than blend.
    if len(candidates) > 1:
        second = candidates[1]

        if (
            second[0] == best[0]
            and second[1] != best[1]
        ):
            return None

    return best


def build_answer(match):
    """Return only the selected policy section and its citation."""
    _, filename, section_number, section_text = match

    return (
        f"{section_text}\n"
        f"Source: {filename}, section {section_number}."
    )


def answer_question(question, indexed):
    """Answer from one source or return the exact refusal."""
    question = question.strip()

    if not question:
        return REFUSAL

    match = find_best_source(question, indexed)

    if match is None:
        return REFUSAL

    return build_answer(match)


def main():
    parser = argparse.ArgumentParser(
        description="UC-X policy document assistant"
    )

    parser.add_argument(
        "--policy-dir",
        default="../data/policy-documents",
        help="Directory containing the policy documents.",
    )

    args = parser.parse_args()

    try:
        indexed = retrieve_documents(args.policy_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return

    print("UC-X policy assistant")
    print("Type a question, or type 'exit' to quit.")
    print()

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if question.lower() in {"exit", "quit"}:
            break

        print()
        print(answer_question(question, indexed))
        print()


if __name__ == "__main__":
    main()