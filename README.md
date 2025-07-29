# Docrobat: Persona-Aware Document Intelligence  
**Challenge 1b – Adobe India Hackathon 2025**

Docrobat is our intelligent and modular solution to Challenge 1b of the Adobe India Hackathon 2025—a persona-aware, context-driven PDF analysis engine. Designed to emulate the way a human researcher would approach large document collections, DotIntel dynamically adapts to the reader’s role (*persona*) and objective (*job-to-be-done*) to extract only the most relevant sections and summaries.

Built for performance, accuracy, and generalization, DotIntel works completely offline, within tight memory and compute constraints—no API calls, no black-box models—just fast, focused document intelligence.


## Core Intelligence Stack

- **PyMuPDF** – Fast, layout-aware PDF parsing  
- **RAKE / spaCy / TF-IDF** – Keyword and anchor term extraction from persona/job description  
- **MiniLM (all-MiniLM-L6-v2)** – Lightweight, high-performance sentence embeddings (~80MB)  
- **FuzzyWuzzy / RapidFuzz** – Approximate string matching for semantic headings  
- **Gensim TextRank** – Offline summarization from candidate text blocks  
- **Heuristic Scoring Engine** – Multi-dimensional logic for ranking document sections  
- **Dockerized** – AMD64, CPU-only, fully offline


## Build & Run with Docker

```bash
# Build the container
docker build --platform linux/amd64 -t dotintel.retriever .

# Run the container
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none dotintel.retriever
````

* Place all input PDFs and the `persona.json` inside the `/input` directory
* The `/output` directory will contain `output.json` in the required format


## Standout Features

### Persona-Aware Relevance Extraction

DotIntel tailors its output based on **who** is reading and **why**:

* Dynamically extracts **anchor topics** using lightweight NLP
* Embeds persona and job as a semantic vector for document matching
* Filters and scores sections that most closely align with the user's intent

### Hybrid Ranking Logic

Section candidates are evaluated using a **multi-factor relevance score**:

| Feature                | Method                                       |
| ---------------------- | -------------------------------------------- |
| **Keyword Match**      | Cosine/Jaccard with anchor term set          |
| **Heading Similarity** | Fuzzy match to job-to-be-done phrasing       |
| **Semantic Relevance** | MiniLM embedding similarity                  |
| **Visual Priority**    | Boosts bold/capitalized sections             |
| **Length Penalty**     | Penalizes overly verbose, low-density chunks |

This ensures accuracy **without** large LLM models or full-text search.

### Offline Subsection Summarization

* Extracts content around high-ranking headings
* Applies **TextRank summarization** to reduce noise
* Outputs focused paragraphs with high semantic overlap



## Project Structure

```
DotIntel/
├── input/                     # Input PDFs + persona.json
├── output/                    # Generated output.json
├── src/
│   ├── extractor.py           # PDF parsing and section indexing
│   ├── scorer.py              # Relevance scoring logic
│   ├── summarizer.py          # TextRank summarization
│   └── main.py                # Pipeline entry point
├── Dockerfile
├── approach_explanation.md
└── README.md
```


## Output Format

Each run produces a structured JSON file like:

```json
{
  "metadata": {
    "documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare a literature review on GNNs for drug discovery",
    "timestamp": "2025-07-28T19:00:00"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "section_title": "Graph Neural Networks for Drug Discovery",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "refined_text": "Graph Neural Networks (GNNs) have emerged as a powerful tool..."
    }
  ]
}
```


## Pass Criteria

* Processes 3–5 PDFs in under **60 seconds**
* Model size under **1GB** (MiniLM is \~80MB)
* All processing is **fully offline**
* Compliant output structure per hackathon specs


## Bonus Features (Optional)

* **Cross-document concept linking**
* **Multilingual filtering** via `langdetect`
* **Persona memory** for adaptive weighting over time
* **Configurable scoring weights** in `config.py`


## Philosophy

Docrobat reflects our belief that intelligent document systems don’t need gigabyte-scale models—they need **purpose awareness**. By aligning structure, semantics, and user context, we create a focused reading assistant that knows *what* to extract and *why*.

> *“Understanding isn’t just parsing—it’s prioritizing what matters.”*


## Team

Made by **Team \[InnovateHers]**
Adobe India Hackathon 2025 – Challenge 1B


