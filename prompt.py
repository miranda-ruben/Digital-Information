
def build_prompt(source_text, question, selected_dates, valid_refusal):
    return f"""
    Answer the user's question using only the official source text below.
    Do not add any facts from your general knowledge.
        First, carefully examine all supplied official sources for information
    relevant to the user's question.
    If any source contains relevant information, answer using that
    information, even if it only answers part of the question.
    Clearly explain which parts are not covered by the sources.
    Never refuse simply because the sources do not answer every part
    of the question.
    Only reply with "{valid_refusal}" if none of the supplied sources
    contains information relevant to the question.
    Sources marked as no longer offered or outdated must be reported as such.
    Answer in plain text.
    Do not use Markdown formatting such as ** or *.
    Cite every factual claim using the exact URL of the official source
    that supports it. Place the citation immediately after the relevant
    information. Never invent or modify URLs or last-checked dates.

    Official source:
    {source_text}

    User question:
    {question}

    Every time you cite a source, include the last checked date of that source in the format "Last checked: DD.MM.YYYY".
    If no date is available, use "Last checked: unknown".
    Last checked dates of the official sources:
    {selected_dates}
    """
