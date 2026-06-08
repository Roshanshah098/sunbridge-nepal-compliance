# nodes/extract.py
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import ComplianceState
from dotenv import load_dotenv
import json
import re
import time

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

EXTRACT_PROMPT = PromptTemplate.from_template("""
You are a technical document analyst. Extract key compliance-relevant fields from the text below.
Return ONLY a valid JSON object. No explanation, no markdown, no extra text.

Extract these fields (use null if not found):
- manufacturer_name         (the actual product manufacturer, not the applicant)
- applicant_name            (the company that applied for the test, may differ from manufacturer)
- manufacturer_address
- product_name
- product_type
- model_numbers             (list all models mentioned)
- rated_power               (list if multiple models)
- input_voltage
- mppt_voltage_range
- output_voltage
- output_frequency
- efficiency                (peak efficiency if mentioned e.g. 96.5%)
- protective_class          (e.g. Class I)
- ambient_temperature       (operating range)
- certifications            (list e.g. CE, IEC 62109-1)
- test_report_number
- test_laboratory
- certificate_number
- date_of_issue
- date_of_expiry
- test_standard             (list e.g. IEC 62109-1:2010, EN 62109-1:2010)
- ip_rating                 (e.g. IP67)
- labeling_info             (what is printed on the product label/marking plate)
- topology                  (e.g. transformerless)
- remarks

If a field is not found, use null.
If multiple values exist, use a list.

PDF TEXT:
{pdf_text}
""")


def _parse_json(raw: str) -> dict:
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"parse_error": raw}


def _merge_fields(base: dict, update: dict) -> dict:
    merged = dict(base)
    for key, val in update.items():
        if key == "parse_error":
            continue
        if merged.get(key) is None and val is not None:
            merged[key] = val
    return merged


def _extract_in_chunks(text: str, chunk_size: int = 3000) -> dict:
    # only use first 12000 chars 
    text   = text[:12000]
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    result = {}
    for i, chunk in enumerate(chunks):
        print(f"[extract] chunk {i+1}/{len(chunks)}...")
        prompt   = EXTRACT_PROMPT.format(pdf_text=chunk)
        response = llm.invoke(prompt)
        fields   = _parse_json(response.content)
        result   = _merge_fields(result, fields)
        time.sleep(12)  # stay within 6000 TPM free tier
    return result


def extract_node(state: ComplianceState) -> dict:

    # PDF1 — large, extract in chunks
    print("[extract] PDF1 — chunked extraction...")
    pdf1_fields = _extract_in_chunks(state["pdf1_text"])
    print(f"[extract] PDF1 done: {list(pdf1_fields.keys())}")

    time.sleep(15)

    # PDF2 — small, single call
    print("[extract] PDF2 — single extraction...")
    prompt2     = EXTRACT_PROMPT.format(pdf_text=state["pdf2_text"][:4000])
    response2   = llm.invoke(prompt2)
    pdf2_fields = _parse_json(response2.content)
    print(f"[extract] PDF2 done: {list(pdf2_fields.keys())}")

    return {
        "pdf1_fields": pdf1_fields,
        "pdf2_fields": pdf2_fields,
    }