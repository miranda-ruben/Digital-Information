
def build_prompt(source_text, question, selected_dates, valid_refusal):
    return f"""
    Answer the user's question using only the official source text below.
    Do not add any facts from your general knowledge.
    If the source contains part of the answer, give that part and say
    clearly what the source does not cover. Do not invent the rest.
    Only if the source contains nothing useful for the question, reply:
    "{valid_refusal}"
    Sources marked as no longer offered or outdated must be reported as such.
    Answer in plain text.
    Do not use Markdown formatting such as ** or *.
    Cite every answer with one or more exact approved official source URLs.

    Official source:
    {source_text}

    User question:
    {question}

    Every time you cite a source, include the last checked date of that source in the format "Last checked: DD.MM.YYYY".
    If no date is available, use "Last checked: unknown".
    Last checked dates of the official sources:
    {selected_dates}
    """
