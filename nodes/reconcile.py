# nodes/reconcile.py
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import ComplianceState
from dotenv import load_dotenv
import json
import re

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


RECONCILE_PROMPT = PromptTemplate.from_template("""
You are a compliance document reviewer preparing an import file for Nepal.

CONTEXT:
- PDF1 is a CB Test Report (IEC/EN 62109-1) issued by SGS for a single-phase inverter.
  The applicant is Zhejiang CHISAGE New Energy Technology Co., Ltd.
  The declared factory/manufacturer is NingBo Deye Inverter Technology Co., Ltd.
- PDF2 is a Certificate of Conformity (COC) issued by SGS for a three-phase grid-connected PV inverter.
  The certificate holder is NingBo Deye Inverter Technology Co., Ltd.
- These two documents may describe different product variants from the same manufacturer group.
  Differences in model numbers and ratings are expected and should be noted clearly, not treated as errors.

Your job is to compare extracted fields and identify:
1. CONSISTENT   — field exists in both and values match or are equivalent
2. MISMATCH     — field exists in both but values differ in a way that needs clarification
3. ONLY_IN_PDF1 — field found only in PDF1
4. ONLY_IN_PDF2 — field found only in PDF2
5. MISSING_BOTH — field is important for Nepal import review but absent in both PDFs

Important fields for Nepal import review (NEPQA 2025 reference):
- manufacturer_name
- manufacturer_address
- product_name
- product_type
- model_numbers
- rated_power
- input_voltage
- output_voltage
- output_frequency
- efficiency
- certifications
- test_report_number
- certificate_number
- date_of_issue
- date_of_expiry
- test_standard
- ip_rating
- labeling_info
- protective_class
- ambient_temperature

Return ONLY a valid JSON object in this exact format. No explanation, no markdown.

{{
  "consistent": {{
      "field_name": "value"
  }},
  "mismatches": [
    {{
      "field":    "field_name",
      "pdf1":     "value from pdf1",
      "pdf2":     "value from pdf2",
      "note":     "short note on the difference"
    }}
  ],
  "only_in_pdf1": {{
      "field_name": "value"
  }},
  "only_in_pdf2": {{
      "field_name": "value"
  }},
  "missing_both": ["field_name_1", "field_name_2"]
}}

PDF1 FIELDS:
{pdf1_fields}

PDF2 FIELDS:
{pdf2_fields}
""")

def _parse_json(raw: str) -> dict:
    raw = re.sub(r"```json|```", "", raw).strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"parse_error": raw}


def reconcile_node(state: ComplianceState) -> dict:

    prompt = RECONCILE_PROMPT.format(
        pdf1_fields=json.dumps(state["pdf1_fields"], indent=2),
        pdf2_fields=json.dumps(state["pdf2_fields"], indent=2),
    )

    response    = llm.invoke(prompt)
    reconciled  = _parse_json(response.content)

    # pull mismatches list out cleanly for state
    mismatches  = reconciled.get("mismatches", [])

    print(f"[reconcile] consistent   : {len(reconciled.get('consistent',   {}))}")
    print(f"[reconcile] mismatches   : {len(mismatches)}")
    print(f"[reconcile] only_in_pdf1 : {len(reconciled.get('only_in_pdf1', {}))}")
    print(f"[reconcile] only_in_pdf2 : {len(reconciled.get('only_in_pdf2', {}))}")
    print(f"[reconcile] missing_both : {reconciled.get('missing_both', [])}")

    return {
        "mismatches": mismatches,
        # store full reconciled result inside pdf1_fields
        # so generate_node can access everything from one place
        "pdf1_fields": {
            **state["pdf1_fields"],
            "_reconciled": reconciled,
        },
    }