skills:
  - name: retrieve_documents
    description: Loads the three supplied policy documents and indexes their numbered sections by document name and section number.
    input: Policy directory path containing policy_hr_leave.txt, policy_it_acceptable_use.txt, and policy_finance_reimbursement.txt.
    output: Structured mapping of document names to numbered policy sections and their source text.
    error_handling: Fails clearly if a required document is missing or contains no numbered sections.

  - name: answer_question
    description: Finds a directly supported answer in one policy document and returns the answer with its document and section citation, or the exact refusal template.
    input: Employee policy question as text plus the indexed policy documents.
    output: Single-source policy answer with document and section citation, or the exact refusal template.
    error_handling: Refuses when the question is unsupported, ambiguous across documents, or cannot be answered without combining sources or adding assumptions.
  