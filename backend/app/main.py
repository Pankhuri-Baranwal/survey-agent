import traceback
import logging
from fastapi import FastAPI, UploadFile, File
from pathlib import Path

from backend.app.services.parser import load_draft, structure_text
from backend.app.services.validator import validate_survey, basic_checks
from backend.app.services.extractor import extract_questions

app = FastAPI(title="Survey Agent - Draft to JSON")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        drafts_dir = Path("drafts")
        drafts_dir.mkdir(exist_ok=True)

        tmp = drafts_dir / file.filename
        tmp.write_bytes(await file.read())

        raw = load_draft(str(tmp))
        structured = structure_text(raw)

        return {
            "chunks_count": len(structured["chunks"]),
            "sample": structured["chunks"][:2]
        }

    except Exception as e:
        logging.error("Error during /ingest:")
        traceback.print_exc()
        return {"error": str(e)}

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """
    Upload a draft file and return canonical survey JSON with validation results.
    """
    try:
        drafts_dir = Path("drafts")
        drafts_dir.mkdir(exist_ok=True)

        tmp = drafts_dir / file.filename
        tmp.write_bytes(await file.read())

        raw = load_draft(str(tmp))
        structured = structure_text(raw)
        survey_json = extract_questions(structured["chunks"])

        valid, schema_errors = validate_survey(survey_json)
        extra_issues = basic_checks(survey_json)

        return {
            "survey_json": survey_json,
            "valid": valid,
            "schema_errors": schema_errors,
            "extra_issues": extra_issues
        }

    except Exception as e:
        logging.error("Error during /extract:")
        traceback.print_exc()
        return {"error": str(e)}