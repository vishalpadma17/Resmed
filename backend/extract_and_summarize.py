import argparse
from pathlib import Path
import PyPDF2
from docx import Document
from transformers import pipeline


SUPPORTED_EXTENSIONS = {".txt", ".docx", ".pdf"}


def extract_text(file_path: str) -> str:
    try:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {suffix}. Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
            )

        if suffix == ".txt":
            return path.read_text(encoding="utf-8", errors="ignore")

        if suffix == ".docx":
            doc = Document(file_path)
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)

        if suffix == ".pdf":
            text_parts = []
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        text_parts.append(page_text)
            return "\n".join(text_parts)

        return ""
    except Exception as e:
        raise RuntimeError(f"Error extracting text from {file_path}: {e}")


def clean_text(text: str) -> str:
    try:
        return " ".join(text.split())
    except Exception as e:
        raise RuntimeError(f"Error cleaning text: {e}")


def chunk_text(text: str, max_chars: int = 2500):
    try:
        text = clean_text(text)
        if not text:
            return []

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + max_chars, text_len)

            if end < text_len:
                last_space = text.rfind(" ", start, end)
                if last_space > start:
                    end = last_space

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end

        return chunks
    except Exception as e:
        raise RuntimeError(f"Error chunking text: {e}")


def build_summarizer(model_name: str):
    try:
        return pipeline("summarization", model=model_name)
    except Exception as e:
        raise RuntimeError(f"Error loading summarization model '{model_name}': {e}")


def summarize_chunks(
    summarizer,
    chunks,
    chunk_max_length: int = 80,
    chunk_min_length: int = 20,
):
    try:
        summaries = []

        for chunk in chunks:
            result = summarizer(
                chunk,
                max_length=chunk_max_length,
                min_length=chunk_min_length,
                do_sample=False,
                truncation=True,
            )
            summaries.append(result[0]["summary_text"])

        return summaries
    except Exception as e:
        raise RuntimeError(f"Error summarizing chunks: {e}")


def summarize_text(
    text: str,
    model_name: str = "sshleifer/distilbart-cnn-12-6",
    chunk_size: int = 2500,
    chunk_max_length: int = 80,
    chunk_min_length: int = 20,
    final_max_length: int = 100,
    final_min_length: int = 25,
) -> str:
    try:
        text = clean_text(text)
        if not text:
            return "No readable text found in the file."

        summarizer = build_summarizer(model_name)
        chunks = chunk_text(text, max_chars=chunk_size)

        if not chunks:
            return "No readable text found in the file."

        chunk_summaries = summarize_chunks(
            summarizer,
            chunks,
            chunk_max_length=chunk_max_length,
            chunk_min_length=chunk_min_length,
        )

        if len(chunk_summaries) == 1:
            return chunk_summaries[0]

        combined_summary_text = " ".join(chunk_summaries)

        final_result = summarizer(
            combined_summary_text,
            max_length=final_max_length,
            min_length=final_min_length,
            do_sample=False,
            truncation=True,
        )

        return final_result[0]["summary_text"]
    except Exception as e:
        raise RuntimeError(f"Error during text summarization: {e}")


def summarize_file(
    file_path: str,
    model_name: str = "sshleifer/distilbart-cnn-12-6",
    chunk_size: int = 2500,
) -> str:
    try:
        text = extract_text(file_path)
        return summarize_text(
            text=text,
            model_name=model_name,
            chunk_size=chunk_size,
        )
    except Exception as e:
        raise RuntimeError(f"Error summarizing file {file_path}: {e}")


def extract_and_summarize(file_path):
    try:
        summary = summarize_file(
            file_path=file_path,
            model_name="sshleifer/distilbart-cnn-12-6",
            chunk_size=2500,
        )
        print("\n=== SUMMARY GENERATED ===\n")
        return summary
    except Exception as e:
        print(f"Error: {e}")
        return(f"Error: {e}")
