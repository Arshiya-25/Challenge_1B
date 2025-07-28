#!/usr/bin/env python3

import os
import json
import logging
import fitz  # PyMuPDF
import re
from typing import List, Dict
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFHeadingExtractor:
    def __init__(self):
        self.font_size_threshold = 2.0
        self.min_heading_size = 10.0
        self.max_heading_length = 200

    def extract_text_with_formatting(self, pdf_path: str) -> List[Dict]:
        try:
            doc = fitz.open(pdf_path)
            text_blocks = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")

                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text:
                                    text_blocks.append({
                                        "text": text,
                                        "size": span["size"],
                                        "flags": span["flags"],
                                        "font": span["font"],
                                        "page": page_num + 1,
                                        "bbox": span["bbox"]
                                    })

            doc.close()
            return text_blocks
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return []

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text).strip()
        text = re.sub(r'[^\w\s\-\.\,\:\;\!\?\(\)\[\]\{\}]', '', text)
        return text

    def is_heading_candidate(self, text: str, size: float, flags: int) -> bool:
        if len(text) < 3 or len(text) > self.max_heading_length:
            return False
        if size < self.min_heading_size:
            return False

        heading_patterns = [
            r'^\d+\.?\s+',
            r'^[A-Z][a-z\s]+$',
            r'^[A-Z\s]+$',
            r'^Chapter\s+\d+',
            r'^Section\s+\d+',
            r'^Part\s+\d+'
        ]
        for pattern in heading_patterns:
            if re.match(pattern, text):
                return True
        if flags & 2**4:
            return True
        return False

    def extract_title(self, text_blocks: List[Dict]) -> str:
        if not text_blocks:
            return "Untitled Document"
        candidates = []
        for block in text_blocks[:10]:
            text = self.clean_text(block["text"])
            if (5 < len(text) < 100 and block["page"] == 1 and not re.match(r'^\d+\.?\s+', text)):
                candidates.append((text, block["size"], block["flags"]))
        if not candidates:
            return "Untitled Document"
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def classify_heading_levels(self, headings: List[Dict]) -> List[Dict]:
        if not headings:
            return []
        headings.sort(key=lambda x: x["size"], reverse=True)
        font_sizes = sorted(set(h["size"] for h in headings), reverse=True)
        level_map = {}
        for i, size in enumerate(font_sizes[:3]):
            level_map[size] = f"H{i+1}"
        result = []
        for h in headings:
            if h["size"] in level_map:
                h["level"] = level_map[h["size"]]
                result.append(h)
        result.sort(key=lambda x: (x["page"], x.get("original_order", 0)))
        return result

    def extract_headings(self, text_blocks: List[Dict]) -> List[Dict]:
        heading_candidates = []
        for i, block in enumerate(text_blocks):
            text = self.clean_text(block["text"])
            if self.is_heading_candidate(text, block["size"], block["flags"]):
                heading_candidates.append({
                    "text": text,
                    "size": block["size"],
                    "flags": block["flags"],
                    "page": block["page"],
                    "original_order": i
                })
        seen = set()
        unique = []
        for h in heading_candidates:
            norm = re.sub(r'\s+', ' ', h["text"]).lower()
            if norm not in seen:
                seen.add(norm)
                unique.append(h)
        return self.classify_heading_levels(unique)

    def process_pdf(self, pdf_path: str) -> Dict:
        logger.info(f"Processing: {pdf_path}")
        text_blocks = self.extract_text_with_formatting(pdf_path)
        if not text_blocks:
            return {"title": "Untitled Document", "outline": []}
        title = self.extract_title(text_blocks)
        headings = self.extract_headings(text_blocks)
        outline = [{"level": h["level"], "text": h["text"], "page": h["page"]} for h in headings]
        return {"title": title, "outline": outline}

def main():
    input_dir = Path("sample_dataset/pdfs")
    output_dir = Path("sample_dataset/outputs")

    output_dir.mkdir(parents=True, exist_ok=True)
    extractor = PDFHeadingExtractor()

    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning("No PDF files found in sample_dataset/pdfs/")
        return

    for pdf_file in pdf_files:
        try:
            result = extractor.process_pdf(str(pdf_file))
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved result to {output_file}")
        except Exception as e:
            logger.error(f"Failed to process {pdf_file}: {str(e)}")
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"title": "Error Processing Document", "outline": []}, f, indent=2)

if __name__ == "__main__":
    main()
