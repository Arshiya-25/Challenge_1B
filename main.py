import os
import json
from pathlib import Path
from datetime import datetime
from utils import (
    parse_persona_and_job,
    extract_headings_from_json,
    score_sections,
    extract_subsections_summary
)

def process_collection(collection_path):
    input_file = collection_path / "challenge1b_input.json"
    output_file = collection_path / "challenge1b_output.json"
    pdf_dir = collection_path / "PDFs"
    heading_dir = collection_path / "heading_jsons"

    if not input_file.exists():
        print(f"[!] Skipping {collection_path.name} — no challenge1b_input.json")
        return

    # Debug: Print file contents
    print(f"[DEBUG] Processing {collection_path.name}")
    print(f"[DEBUG] Input file path: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        
        # Debug: Print the entire JSON structure
        print(f"[DEBUG] JSON contents: {json.dumps(input_data, indent=2)}")
        
    except json.JSONDecodeError as e:
        print(f"[!] JSON decode error in {collection_path.name}: {e}")
        return
    except Exception as e:
        print(f"[!] Error reading file {collection_path.name}: {e}")
        return

    # Check all possible key variations
    persona = None
    job = None
    
    # Try different possible key names
    persona_keys = ["persona", "Persona", "PERSONA", "user_persona", "target_persona"]
    job_keys = ["job_to_be_done", "job", "Job", "JOB", "task", "objective", "job_description"]
    
    for key in persona_keys:
        if key in input_data and input_data[key]:
            persona = input_data[key]
            print(f"[DEBUG] Found persona with key '{key}': {persona}")
            break
    
    for key in job_keys:
        if key in input_data and input_data[key]:
            job = input_data[key]
            print(f"[DEBUG] Found job with key '{key}': {job}")
            break
    
    # If still not found, print available keys
    if not persona or not job:
        print(f"[DEBUG] Available keys in JSON: {list(input_data.keys())}")
        
    if not persona:
        print(f"[!] No persona found in {collection_path.name}")
        return
        
    if not job:
        print(f"[!] No job found in {collection_path.name}")
        return

    # Check if PDF and heading directories exist
    if not pdf_dir.exists():
        print(f"[!] PDF directory not found: {pdf_dir}")
        return
        
    if not heading_dir.exists():
        print(f"[!] Heading directory not found: {heading_dir}")
        return

    documents = list(pdf_dir.glob("*.pdf"))
    print(f"[DEBUG] Found {len(documents)} PDF files")
    
    if not documents:
        print(f"[!] No PDF files found in {pdf_dir}")
        return

    anchor_keywords = parse_persona_and_job(persona, job)
    print(f"[DEBUG] Extracted keywords: {anchor_keywords}")

    section_scores = []
    subsection_analysis = []

    for pdf_file in documents:
        heading_file = heading_dir / f"{pdf_file.stem}.json"
        if not heading_file.exists():
            print(f"[!] Heading JSON not found for {pdf_file.name}")
            continue

        print(f"[DEBUG] Processing {pdf_file.name}")
        headings = extract_headings_from_json(heading_file)
        print(f"[DEBUG] Found {len(headings)} headings")
        
        if not headings:
            print(f"[!] No headings found in {heading_file}")
            continue

        ranked_sections = score_sections(headings, anchor_keywords)

        for sec in ranked_sections:
            section_scores.append({
                "document": pdf_file.name,
                "page_number": sec["page"],
                "section_title": sec["text"],
                "importance_rank": sec["rank"]
            })

            summary = extract_subsections_summary(pdf_file, sec["page"], sec["text"])
            subsection_analysis.append({
                "document": pdf_file.name,
                "page_number": sec["page"],
                "refined_text": summary
            })

    result = {
        "metadata": {
            "documents": [doc.name for doc in documents],
            "persona": persona,
            "job_to_be_done": job,
            "timestamp": datetime.now().isoformat()
        },
        "extracted_sections": section_scores,
        "subsection_analysis": subsection_analysis
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"[✓] Output written to {output_file.name}")

def main():
    base_dir = Path(".")
    collections = [p for p in base_dir.iterdir() if p.is_dir() and p.name.startswith("Collection")]
    
    print(f"[DEBUG] Found {len(collections)} collections")
    for collection in collections:
        print(f"[DEBUG] Collection path: {collection}")

    for collection in collections:
        process_collection(collection)

if __name__ == "__main__":
    main()