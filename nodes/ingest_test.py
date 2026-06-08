# nodes/ingest.py
from langchain_community.document_loaders import PDFPlumberLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from state import ComplianceState
import re
from dotenv import load_dotenv
import os

load_dotenv()

PDF1_PATH = os.getenv("PDF1_PATH")
PDF2_PATH = os.getenv("PDF2_PATH")


load_dotenv()
print("PDF1:", os.getenv("PDF1_PATH"))
print("PDF2:", os.getenv("PDF2_PATH"))

def clean_text(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    return text.strip()


def ingest_node(state: ComplianceState) -> dict:

    # --- for PDF 1 : tabular 
    loader1 = PDFPlumberLoader(PDF1_PATH)
    docs1   = loader1.load()
    for doc in docs1:
        doc.page_content = clean_text(doc.page_content)

    total_chars1 = sum(len(d.page_content) for d in docs1)

    if total_chars1 < 5_000:
        chunk_size1, chunk_overlap1 = 500,  50
    elif total_chars1 < 20_000:
        chunk_size1, chunk_overlap1 = 800,  150
    elif total_chars1 < 50_000:
        chunk_size1, chunk_overlap1 = 1000, 200
    elif total_chars1 < 100_000:
        chunk_size1, chunk_overlap1 = 1200, 250
    else:
        chunk_size1, chunk_overlap1 = 1500, 300

    splitter1 = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size1,
        chunk_overlap=chunk_overlap1,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks1   = splitter1.split_documents(docs1)
    pdf1_text = "\n\n".join(c.page_content for c in chunks1)

    print(f"[ingest] PDF1 — pages: {len(docs1)} | chars: {total_chars1} | chunks: {len(chunks1)}")

    # --- PDF 2 : for certificate list and textual
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