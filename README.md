## Approach Explanation for 1B: Persona-Driven Document Intelligence

We build an intelligent document analyzer that extracts relevant sections based on persona and task, using structured outputs from 1A.

### Step-by-Step:
1. **Persona Understanding:**
   - Extract keywords from the persona and task description.
   - These keywords form the semantic core for document matching.

2. **Section Indexing:**
   - We use pre-parsed heading JSON files from Round 1A.
   - Headings (H1, H2, H3) are extracted and indexed per document.

3. **Relevance Scoring:**
   - For each heading, compute TF-IDF-based cosine similarity with persona-task keywords.
   - Rank top-5 headings across documents.

4. **Subsection Analysis:**
   - Extract text around selected headings (same page).
   - Summarize using simple sentence selection.

### Output
The final JSON output includes:
- Metadata (timestamp, persona, job, input docs)
- Ranked relevant sections
- Refined subsection summaries

### Constraints
- All modules run offline (no API calls)
- CPU-compliant, <1GB RAM footprint
- ≤ 60 seconds for up to 5 PDFs

### Extensibility
- Can integrate TextRank summarization
- Persona embedding via offline MiniLM model for better matching
