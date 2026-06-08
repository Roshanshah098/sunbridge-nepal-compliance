# nodes/ingest.py
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from state import ComplianceState
from dotenv import load_dotenv
import pymupdf4llm
import re
import os

load_dotenv()

PDF1_PATH = os.getenv("PDF1_PATH")
PDF2_PATH = os.getenv("PDF2_PATH")

print("PDF1:", PDF1_PATH)
print("PDF2:", PDF2_PATH)


def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


def ingest_node(state: ComplianceState) -> dict:

    # PDF1 — image-based CB test report, using pymupdf4llm
    # To -- ramro saanga hernu -- handles scanned tables, marking plates, clause/result tables
    raw1      = pymupdf4llm.to_markdown(PDF1_PATH)
    pdf1_text = clean_text(raw1)
    print(f"[ingest] PDF1 — chars: {len(pdf1_text)}")

    # PDF2 — clean text COC certificate, using PyMuPDFLoader
    loader2 = PyMuPDFLoader(PDF2_PATH)
    docs2   = loader2.load()
    for doc in docs2: 
        doc.page_content = clean_text(doc.page_content)

    total_chars2 = sum(len(d.page_content) for d in docs2)

    if total_chars2 < 5_000:
        chunk_size2, chunk_overlap2 = 500,  50
    elif total_chars2 < 20_000:
        chunk_size2, chunk_overlap2 = 800,  150
    elif total_chars2 < 50_000:
        chunk_size2, chunk_overlap2 = 1000, 200
    elif total_chars2 < 100_000:
        chunk_size2, chunk_overlap2 = 1200, 250
    else:
        chunk_size2, chunk_overlap2 = 1500, 300

    splitter2 = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size2,
        chunk_overlap=chunk_overlap2,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks2   = splitter2.split_documents(docs2)
    pdf2_text = "\n\n".join(c.page_content for c in chunks2)

    print(f"[ingest] PDF2 — pages: {len(docs2)} | chars: {total_chars2} | chunks: {len(chunks2)}")

    return {
        "pdf1_text": pdf1_text,
        "pdf2_text": pdf2_text,
    }