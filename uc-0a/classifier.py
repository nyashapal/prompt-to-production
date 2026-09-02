"""
UC-0A — Complaint Classifier

Classifies citizen complaints using the fixed UC-0A taxonomy
and the required severity rules.
"""

import argparse
import csv


# Exact category values required by the UC-0A README.
ALLOWED_CATEGORIES = {
    "Pothole",
    "Flooding",
    "Streetlight",
    "Waste",
    "Noise",
    "Road Damage",
    "Heritage Damage",
    "Heat Hazard",
    "Drain Blockage",
    "Other",
}


# Exact severity keywords required to trigger Urgent.
URGENT_KEYWORDS = [
    "injury",
    "child",
    "school",
    "hospital",
    "ambulance",
    "fire",
    "hazard",
    "fell",
    "collapse",
]


def classify_complaint(row: dict) -> dict:
    """
    Classify one complaint.

    Returns:
        complaint_id
        category
        priority
        reason
        flag
    """

    complaint_id = str(row.get("complaint_id") or "").strip()
    description = str(row.get("description") or "").strip()

    # Missing description cannot be classified reliably.
    if not description:
        return {
            "complaint_id": complaint_id,
            "category": "Other",
            "priority": "Low",
            "reason": "The description is missing.",
            "flag": "NEEDS_REVIEW",
        }

    text = description.lower()

    # -------------------------------------------------
    # CATEGORY
    # -------------------------------------------------

    # Check specific categories before broader categories.
    if any(word in text for word in [
        "drain blocked",
        "blocked drain",
        "drain blockage",
        "clogged drain",
    ]):
        category = "Drain Blockage"

    elif "pothole" in text:
        category = "Pothole"

    elif any(word in text for word in [
        "flood",
        "flooded",
        "flooding",
        "waterlogged",
        "water logged",
    ]):
        category = "Flooding"

    elif any(word in text for word in [
        "streetlight",
        "streetlights",
        "street light",
        "lights out",
    ]):
        category = "Streetlight"

    elif any(word in text for word in [
        "heritage damage",
        "heritage building",
        "historic building",
        "historical building",
    ]):
        category = "Heritage Damage"

    elif any(word in text for word in [
        "heat hazard",
        "extreme heat",
        "heatwave",
        "heat wave",
    ]):
        category = "Heat Hazard"

    elif any(word in text for word in [
        "music past midnight",
        "loud music",
        "noise",
        "noisy",
    ]):
        category = "Noise"

    elif any(word in text for word in [
        "road surface",
        "road crack",
        "road cracked",
        "sinking",
        "road damage",
    ]):
        category = "Road Damage"

    elif any(word in text for word in [
        "garbage",
        "waste",
        "rubbish",
        "trash",
        "dumped",
        "dumping",
    ]):
        category = "Waste"

    else:
        category = "Other"

    # -------------------------------------------------
    # PRIORITY
    # -------------------------------------------------

    # README requires Urgent whenever one of these
    # severity keywords appears.
    matched_keyword = next(
        (keyword for keyword in URGENT_KEYWORDS if keyword in text),
        None
    )

    if matched_keyword:
        priority = "Urgent"
        reason = (
            f'The description contains "{matched_keyword}", '
            "which triggers the urgent severity rule."
        )
    else:
        priority = "Standard"

        # Use a specific phrase from the description rather
        # than copying the whole complaint.
        first_sentence = description.split(".")[0].strip()

        if not first_sentence:
            first_sentence = description

        # Keep the reason to one sentence.
        reason = (
            f'The phrase "{first_sentence}" supports the '
            f"{category} classification."
        )

    # -------------------------------------------------
    # FLAG
    # -------------------------------------------------

    # Blank means no review is needed.
    flag = ""

    # Final taxonomy safety check.
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
        flag = "NEEDS_REVIEW"

    return {
        "complaint_id": complaint_id,
        "category": category,
        "priority": priority,
        "reason": reason,
        "flag": flag,
    }


def batch_classify(input_path: str, output_path: str):
    """
    Read input CSV, classify every complaint, and write results.

    A bad individual row must not stop the entire batch.
    """

    output_fields = [
        "complaint_id",
        "category",
        "priority",
        "reason",
        "flag",
    ]

    with open(
        input_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as infile:

        reader = csv.DictReader(infile)

        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline=""
        ) as outfile:

            writer = csv.DictWriter(
                outfile,
                fieldnames=output_fields
            )

            writer.writeheader()

            for row in reader:
                try:
                    result = classify_complaint(row)

                except Exception as exc:
                    result = {
                        "complaint_id": str(
                            row.get("complaint_id") or ""
                        ).strip(),
                        "category": "Other",
                        "priority": "Low",
                        "reason": (
                            f"Classification failed because {exc}."
                        ),
                        "flag": "NEEDS_REVIEW",
                    }

                writer.writerow(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="UC-0A Complaint Classifier"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to test_[city].csv"
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to write results CSV"
    )

    args = parser.parse_args()

    batch_classify(args.input, args.output)

    print(f"Done. Results written to {args.output}")