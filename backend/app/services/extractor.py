import re
from typing import List, Dict

def infer_question_type(chunk: str) -> str:
    """
    Naive heuristic to guess question type from text.
    Later you can replace this with an LLM call.
    """
    lines = chunk.splitlines()
    # If options are listed with dashes, assume single-select
    if any(re.search(r"^-", l) for l in lines[1:]):
        return "single_select"
    # If the word 'matrix' appears, assume matrix type
    if "matrix" in chunk.lower():
        return "matrix"
    # If 'open' or 'comment' appears, assume open text
    if "open" in chunk.lower() or "comment" in chunk.lower():
        return "open_text"
    # Otherwise unknown
    return "unknown"

def extract_questions(chunks: List[str]) -> Dict:
    questions = []
    for i, chunk in enumerate(chunks, start=1):
        qtype = infer_question_type(chunk)
        options = []
        for line in chunk.splitlines()[1:]:
            if line.strip().startswith("-"):
                options.append(line.strip("- ").strip())

        questions.append({
            "id": f"Q{i}",
            "text": chunk.splitlines()[0],
            "type": qtype,
            "options": options if options else None,
            "needs_review": qtype == "unknown"
        })

    return {
        "title": "Auto-generated survey",
        "language": "en",
        "questions": questions
    }