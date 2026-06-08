# sunbridge-nepal-compliance

A LangGraph-based AI pipeline that reads two Chinese manufacturer PDFs for a solar inverter, reconciles the data field by field, and generates a Nepal import compliance draft for SunBridge Trading, Kathmandu.

---

## What it does

1. **Ingest** — loads both PDFs, cleans and chunks the text
2. **Extract** — LLM pulls structured fields from each PDF
3. **Reconcile** — compares fields, flags mismatches and missing data
4. **Generate** — writes a structured compliance draft referencing NEPQA 2025

---

## PDF Loaders

| PDF                                       | Loader             | Reason                    |
| ----------------------------------------- | ------------------ | ------------------------- |
| PDF1 — CB Test Report (70+ pages, tables) | `PDFPlumberLoader` | Preserves table structure |
| PDF2 — COC Certificate (4 pages, text)    | `PyMuPDFLoader`    | Clean text extraction     |

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
PDF1_PATH=data/pdf1.pdf
PDF2_PATH=data/pdf2.pdf
```

Place your two manufacturer PDFs in `data/`.

---

## Run

```bash
python graph.py
```

Output lands in `output/nepal_compliance_draft.md`.

---

## Stack

- **LangGraph** — 4-node linear pipeline
- **LangChain** — PDF loaders, prompt templates
- **Groq (llama-3.3-70b-versatile)** — extraction, reconciliation, report generation
- **PDFPlumber + PyMuPDF** — PDF parsing

---

## Project structure

```
sunbridge-nepal-compliance/
├── graph.py
├── state.py
├── nodes/
│   ├── ingest.py
│   ├── extract.py
│   ├── reconcile.py
│   └── generate.py
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Notes

- NEPQA 2025 is used as import-side reference only — not fed to the LLM as source data
- `.env`, `data/`, and `output/` are excluded from the repo
- Draft output is marked for agent review, not final filing
