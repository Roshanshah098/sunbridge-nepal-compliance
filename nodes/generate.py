 # nodes/generate.py
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from state import ComplianceState
from dotenv import load_dotenv
from datetime import date
import json

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.3)


GENERATE_PROMPT = PromptTemplate.from_template("""
You are a compliance document writer preparing a Nepal import review draft for SunBridge Trading.

The product is a grid-tied solar inverter being imported from China into Nepal.
Use the reconciled data below to write a clear, honest compliance draft.

Reference standard (import-side): NEPQA 2025 (Nepal)
Use it only as a guide for what Nepal import reviews typically ask for.
Do NOT copy it section by section. Write naturally based on the data available.

Today's date: {today}

---

RECONCILED DATA:
{reconciled}

---

MISMATCH LIST:
{mismatches}

---

Write the compliance draft in this structure:

1. DOCUMENT HEADER
   - Prepared for   : SunBridge Trading, Kathmandu
   - Prepared by    : AI Compliance Draft (for agent review)
   - Date           : today
   - Status         : Draft — pending agent verification

2. PRODUCT INFORMATION
   - Product name, type, model numbers
   - Manufacturer name and address
   - Note any variant differences found across the two source PDFs
   - Note if applicant name differs from manufacturer name — this is relevant for Nepal import review

3. TECHNICAL SPECIFICATIONS
   - Rated power, input voltage, output voltage, output frequency, efficiency
   - IP rating
   - Note any missing or unconfirmed specs clearly

4. TEST AND CERTIFICATION INFORMATION
   - Test report number, certificate number
   - Date of issue, date of expiry
   - Certifications held (list)
   - Test standards referenced
   - Flag anything missing or expired

5. LABELING INFORMATION
   - What labeling info was found
   - What is missing or unclear

6. CONSISTENCY REVIEW
   - Fields that are consistent across both source PDFs
   - Fields that MISMATCH — show both values side by side, with a short note
   - Fields found in only one source
   - Fields missing from both sources (important for Nepal review)

7. ITEMS REQUIRING CLARIFICATION
   - List anything the Nepal import agent or SunBridge should follow up on
   - Be specific — e.g. "PDF1 shows efficiency as 96.5% but PDF2 does not mention it"

8. PREPARER'S NOTE
   - Short honest note on how this draft was prepared
   - Mention that two manufacturer PDFs were used as source data
   - Mention that NEPQA 2025 was used as import-side reference only
   - Note that this is a work-in-progress for agent review, not a final filing

Use plain English. Be specific. Where data is missing, say so clearly.
Do not invent or assume values not found in the source data.
""")


def generate_node(state: ComplianceState) -> dict:

    reconciled = state["pdf1_fields"].get("_reconciled", {})
    mismatches = state.get("mismatches", [])

    prompt = GENERATE_PROMPT.format(
        today      = date.today().strftime("%B %d, %Y"),
        reconciled = json.dumps(reconciled, indent=2),
        mismatches = json.dumps(mismatches, indent=2),
    )

    response = llm.invoke(prompt)
    report   = response.content

    # save to file
    output_path = "output/nepal_compliance_draft.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[generate] Report written to {output_path}")

    return {"report": report}