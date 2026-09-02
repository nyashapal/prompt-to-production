"""
UC-0C — Number That Looks Right

Calculates growth for one explicitly requested ward and category.
Null actual_spend values are flagged rather than silently ignored.
"""

import argparse
import csv
import sys


REQUIRED_COLUMNS = {
    "period",
    "ward",
    "category",
    "budgeted_amount",
    "actual_spend",
    "notes",
}


def load_dataset(input_path):
    """Load and validate the budget CSV."""

    try:
        with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError("Input CSV has no header.")

            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError(
                    "Missing required columns: " + ", ".join(sorted(missing))
                )

            rows = list(reader)

    except FileNotFoundError:
        raise ValueError(f"Input file not found: {input_path}")
    except OSError as exc:
        raise ValueError(f"Could not read input file: {exc}")

    null_rows = []

    for row in rows:
        actual = (row.get("actual_spend") or "").strip()

        if actual == "":
            null_rows.append(
                {
                    "period": row.get("period", ""),
                    "ward": row.get("ward", ""),
                    "category": row.get("category", ""),
                    "reason": row.get("notes", "").strip(),
                }
            )

    return rows, null_rows


def compute_growth(rows, ward, category, growth_type):
    """
    Calculate growth for one ward/category.

    Currently supported:
      MoM = (current_month - previous_month) / previous_month * 100
    """

    if not ward:
        raise ValueError("Ward must be explicitly supplied.")

    if not category:
        raise ValueError("Category must be explicitly supplied.")

    if not growth_type:
        raise ValueError(
            "Growth type must be explicitly supplied; refusing to guess."
        )

    if growth_type != "MoM":
        raise ValueError(
            f"Unsupported growth type '{growth_type}'. "
            "This implementation supports only MoM."
        )

    selected = [
        row
        for row in rows
        if row.get("ward", "").strip() == ward
        and row.get("category", "").strip() == category
    ]

    if not selected:
        raise ValueError(
            f"No data found for ward '{ward}' and category '{category}'."
        )

    selected.sort(key=lambda row: row.get("period", ""))

    results = []
    previous_actual = None
    previous_period = None

    for row in selected:
        period = row.get("period", "").strip()
        actual_text = (row.get("actual_spend") or "").strip()
        notes = row.get("notes", "").strip()

        if actual_text == "":
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": "",
                    "growth_type": growth_type,
                    "growth": "",
                    "formula": "NOT COMPUTED",
                    "flag": "NULL_ACTUAL_SPEND",
                    "reason": notes or "actual_spend is null",
                }
            )

            previous_actual = None
            previous_period = period
            continue

        try:
            current_actual = float(actual_text)
        except ValueError:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": actual_text,
                    "growth_type": growth_type,
                    "growth": "",
                    "formula": "NOT COMPUTED",
                    "flag": "INVALID_ACTUAL_SPEND",
                    "reason": "actual_spend is not a valid number",
                }
            )

            previous_actual = None
            previous_period = period
            continue

        # The first period has no previous period, so growth cannot be computed.
        if previous_actual is None:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{current_actual:g}",
                    "growth_type": growth_type,
                    "growth": "",
                    "formula": "NOT COMPUTED — no previous period",
                    "flag": "NO_PREVIOUS_PERIOD",
                    "reason": "No previous period is available for comparison.",
                }
            )
        elif previous_actual == 0:
            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{current_actual:g}",
                    "growth_type": growth_type,
                    "growth": "",
                    "formula": (
                        f"({current_actual:g} - {previous_actual:g}) "
                        f"/ {previous_actual:g} × 100"
                    ),
                    "flag": "DIVISION_BY_ZERO",
                    "reason": "Previous actual_spend is zero.",
                }
            )
        else:
            growth = (
                (current_actual - previous_actual)
                / previous_actual
                * 100
            )

            results.append(
                {
                    "period": period,
                    "ward": ward,
                    "category": category,
                    "actual_spend": f"{current_actual:g}",
                    "growth_type": growth_type,
                    "growth": f"{growth:+.1f}%",
                    "formula": (
                        f"({current_actual:g} - {previous_actual:g}) "
                        f"/ {previous_actual:g} × 100"
                    ),
                    "flag": "",
                    "reason": "",
                }
            )

        previous_actual = current_actual
        previous_period = period

    return results


def write_output(output_path, results):
    """Write the per-period results CSV."""

    fieldnames = [
        "period",
        "ward",
        "category",
        "actual_spend",
        "growth_type",
        "growth",
        "formula",
        "flag",
        "reason",
    ]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser(
        description="UC-0C Budget Growth Calculator"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to ward_budget.csv",
    )

    parser.add_argument(
        "--ward",
        required=True,
        help="Exact ward name",
    )

    parser.add_argument(
        "--category",
        required=True,
        help="Exact category name",
    )

    parser.add_argument(
        "--growth-type",
        required=True,
        help="Growth calculation type; currently supported: MoM",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CSV",
    )

    args = parser.parse_args()

    try:
        rows, null_rows = load_dataset(args.input)

        print(f"Loaded {len(rows)} rows.")

        if null_rows:
            print(f"Found {len(null_rows)} null actual_spend rows.")

            for item in null_rows:
                print(
                    f"NULL: {item['period']} | "
                    f"{item['ward']} | "
                    f"{item['category']} | "
                    f"{item['reason']}"
                )

        results = compute_growth(
            rows,
            args.ward,
            args.category,
            args.growth_type,
        )

        write_output(args.output, results)

        print(
            f"Done. Growth results written to {args.output}"
        )

    except ValueError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
