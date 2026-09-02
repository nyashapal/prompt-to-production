skills:

&#x20; - name: retrieve\_documents

&#x20;   description: Loads the three supplied policy documents and indexes their numbered sections by document name and section number.

&#x20;   input: Policy directory path containing the three required policy files.

&#x20;   output: Dictionary mapping each document filename to its numbered sections and section text.

&#x20;   error\_handling: Fails clearly if a required document is missing or contains no numbered sections.



&#x20; - name: answer\_question

&#x20;   description: Answers a policy question using exactly one policy document section or returns the exact refusal template.

&#x20;   input: User question and indexed policy documents.

&#x20;   output: Source-grounded answer with document and section citation, or the exact refusal template.

&#x20;   error\_handling: Refuses when the evidence is ambiguous, unsupported, or would require combining documents.

