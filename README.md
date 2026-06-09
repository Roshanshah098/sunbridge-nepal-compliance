# sunbridge-nepal-compliance

A LangGraph-based AI pipeline that reads two Chinese manufacturer PDFs for a solar inverter, reconciles the data field by field, and generates a Nepal import compliance draft for SunBridge Trading, Kathmandu.

---

## What it does

1. **Ingest** — loads both PDFs using appropriate loaders, runs OCR on the image-based CB Test Report, cleans and chunks the text
2. **Extract** — LLM pulls structured compliance fields from each PDF in chunks (to stay within Groq free tier TPM limits)
3. **Reconcile** — compares fields side by side, flags mismatches, missing data, and fields found in only one source
4. **Generate** — writes a structured 8-section compliance draft referencing NEPQA 2025 as import-side guide

---

## PDF Loaders

| PDF                                                           | Loader          | Reason                                                                           |
| ------------------------------------------------------------- | --------------- | -------------------------------------------------------------------------------- |
| PDF1 — CB Test Report (72 pages, image-based, scanned tables) | `pymupdf4llm`   | Runs Tesseract OCR, extracts scanned tables and marking plates as clean markdown |
| PDF2 — COC Certificate (4 pages, clean text)                  | `PyMuPDFLoader` | Standard text extraction, no OCR needed                                          |

---

## Setup

```bash
git clone https://github.com/Roshanshah098/sunbridge-nepal-compliance.git
cd sunbridge-nepal-compliance
pip install -r requirements.txt
```

Create a `.env` file:

```
GROQ_API_KEY=your_key_here
PDF1_PATH=path/to/pdf1.pdf
PDF2_PATH=path/to/pdf2.pdf
```

Place your two manufacturer PDFs at the paths specified in `.env`.

---

## Run

```bash
python graph.py
```

Output lands in `output/nepal_compliance_draft.md`.

---

## Stack

- **LangGraph** — 4-node linear pipeline (StateGraph)
- **LangChain** — PDF loaders, prompt templates
- **Groq** (`llama-3.3-70b-versatile`) — field extraction, reconciliation, report generation
- **pymupdf4llm + Tesseract** — OCR for image-based PDF1
- **PyMuPDF** — text extraction for PDF2

---

## Project structure

```
sunbridge-nepal-compliance/
├── graph.py            ← entry point, builds and runs the pipeline
├── state.py            ← shared ComplianceState between nodes
├── nodes/
│   ├── ingest.py       ← loads and cleans both PDFs
│   ├── extract.py      ← LLM extracts fields in chunks
│   ├── reconcile.py    ← compares fields, flags mismatches
│   └── generate.py     ← writes the compliance draft
├── output/             ← generated report lands here
├── .env                ← API keys and PDF paths (not committed)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Source documents

| File                                  | Type                            | Description                                                                                   |
| ------------------------------------- | ------------------------------- | --------------------------------------------------------------------------------------------- |
| `DSS_GZES230100125901_combined-1.pdf` | CB Test Report                  | IEC/EN 62109-1, single-phase inverter, applicant: Zhejiang CHISAGE, manufacturer: NingBo Deye |
| `188_1115.pdf`                        | Certificate of Conformity (COC) | SGS PCS-24-1022, grid-connected PV inverter, NingBo Deye, models SUN-3K to SUN-15K            |

---

## Key findings from the pipeline

- **8 mismatches** detected — manufacturer name, address, model numbers, certifications, test report numbers, input voltage, dates of issue
- **Different product variants** — PDF1 covers single-phase CE-series models, PDF2 covers three-phase SUN-series models from the same manufacturer group
- **Missing from both** — efficiency not explicitly stated in either document
- **Compliance flag** — applicant (Zhejiang CHISAGE) differs from declared factory (NingBo Deye) in PDF1

---

## Notes

- NEPQA 2025 is used as import-side reference only — not fed to the LLM as source data
- PDF paths and API keys are kept local via `.env` — not committed to the repo
- Draft output is marked for agent review, not final filing
- Groq free tier TPM limit (6,000 tokens/minute) handled via chunked extraction with sleep between calls
