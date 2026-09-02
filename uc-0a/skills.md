# UC-0A Complaint Classifier Skills

skills:

  - name: classify_complaint
    description: >
      Classifies one citizen complaint using the fixed UC-0A category
      taxonomy and severity rules.

    input: >
      One complaint row represented as a dictionary containing at least
      complaint_id and description fields.

    output: >
      A dictionary containing complaint_id, category, priority, reason,
      and flag.

    error_handling: >
      If the description is missing, invalid, or genuinely ambiguous,
      return category Other and flag NEEDS_REVIEW instead of crashing.

  - name: batch_classify
    description: >
      Reads a complaint CSV, applies classify_complaint to every row,
      and writes the classification results to an output CSV.

    input: >
      An input CSV file path containing complaint rows and an output CSV
      file path where the results should be written.

    output: >
      A CSV containing complaint_id, category, priority, reason, and flag
      for every input row.

    error_handling: >
      Invalid individual rows must not stop the batch process. The affected
      row should be written with category Other and flag NEEDS_REVIEW.