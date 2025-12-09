import json
from pathlib import Path
from jsonschema import Draft202012Validator

# Load the canonical survey schema once at import
schema_path = Path(__file__).parent.parent / "schema" / "survey_schema.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))

def validate_survey(survey_json: dict):
    """
    Validate a survey JSON object against the canonical schema.
    Returns (is_valid, list_of_errors).
    """
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(survey_json), key=lambda e: e.path)
    msgs = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors]
    return (len(msgs) == 0, msgs)

def basic_checks(survey_json: dict) -> list:
    """
    Perform extra sanity checks beyond schema validation.
    Returns a list of issues found.
    """
    issues = []

    # Ensure question IDs are unique
    ids = [q.get("id") for q in survey_json.get("questions", []) if "id" in q]
    if len(ids) != len(set(ids)):
        issues.append("Duplicate question IDs detected.")

    # Ensure select-type questions have options
    for q in survey_json.get("questions", []):
        qid = q.get("id", "<unknown>")
        qtype = q.get("type")
        if qtype in ["single_select", "multi_select"] and not q.get("options"):
            issues.append(f"Question {qid} missing options for {qtype}.")

        # Ensure matrix questions have rows and columns
        if qtype == "matrix":
            if not q.get("rows") or not q.get("columns"):
                issues.append(f"Question {qid} matrix must have both rows and columns.")

    return issues