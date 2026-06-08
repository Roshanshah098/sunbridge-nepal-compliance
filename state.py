# state.py
from typing import TypedDict, Optional


class ComplianceState(TypedDict):
    pdf1_text: str
    pdf2_text: str
    pdf1_fields: dict
    pdf2_fields: dict
    mismatches: list
    report: str
