# Chapter 5 Slides

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

**Session 5:** Map: Navigating Multimodal RAG

Jason Liu

---

## Today's Goals

**From Segmentation to Specialized Solutions**

- Build specific indices for specific problems
- Two classes of improvements for RAG systems
- Navigate multimodal data: documents, images, tables
- Essential metrics for search index performance
- Prepare for unified routing system (Session 6)

**Focus: Solving individual user experiences one at a time**

---

## Progress Review: Sessions 1-4

**Sessions 1-3: Foundation Building**
- **Session 1:** RAG playbook, synthetic data generation
- **Session 2:** Fine-tuning for relevancy improvements
- **Session 3:** User experience to collect more data

**Session 4: Split Strategy**
- Built segmentation models for users and queries
- Prioritized segments by impact, volume, probability of success
- Identified new capabilities through data analysis

**Today: Map Strategy - Solve each segment individually**

---

## Core Philosophy: Local vs Global Models

**Key Principle:** When segments exist in a population, local solutions outperform global ones

**Why Build Specific Indices?**
- **Division of Labor:** Teams can work on isolated problems
- **Scalability:** Adding new indices easier than rebuilding systems
- **Performance:** Specialized solutions beat general purpose
- **Organization:** Clear separation of concerns

> "Instead of one search index, split the problem space and solve each locally"

**Real-World Reference:** Google has been doing this for years
- Google Maps (location queries)
- Google Photos (image searches) 
- YouTube (video content)
- Web (general text)
- Shopping (product searches)

Google's router decides which tool to show based on your search intent

---

## Real-World Example: Hardware Store Search

**Three Different Search Needs:**

### Lexical Search
```
"How does the XZF2000 compare to the XZF3000?"
```
Serial numbers don't embed well - need exact matching

### Semantic Search  
```
"What do people think about this saw's durability?"
```
Opinion and sentiment queries need semantic understanding

### Structured Search
```
"How much does it weigh? What's the latest version?"
```
Spec queries need text-to-SQL over manufacturer data

---

## Building a Simple Router

**Function Calling with Instructor:**

```python
from instructor import patch
from openai import OpenAI

# Parallel tool calling
tools = [
    WeatherTool,
    GoogleSearchTool,
    ProductSearchTool
]

# Route query to appropriate tools
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": query}],
    tools=tools,
    tool_choice="auto"
)
```

**Execute in parallel → Collect results → Synthesize answer**

---

## Combining Multiple Search Results

### Short-term Approach
1. Concatenate results from all relevant indices
2. Apply reranker to results
3. Stuff everything into context
4. Generate final response

### Long-term Approach
```python
# Train ranking model with multiple signals
final_score = (
    w1 * cosine_similarity_score +
    w2 * cohere_rerank_score +
    w3 * authority_score +
    w4 * freshness_score +
    w5 * citation_score
)
```

---

## Critical Performance Insight

**The Fundamental Equation:**
```
P(correct chunk found) = P(correct chunk | correct retriever) × P(correct retriever)
```

**This Session:** Focus on `P(correct chunk | correct retriever)`  
**Next Session:** Focus on `P(correct retriever)`

**Debugging Strategy:**
- If routing fails → Better prompts, examples  
- If retrieval fails → Better embeddings, filtering

**The Process:**
1. Test retrieval in global sense
2. Once happy, figure out clusters through segmentation
3. Prioritize segments by impact, volume, probability of success
4. Build specialized retrievers
5. Measure if retriever finds right data (precision/recall)
6. Measure if LM chooses right tools

**Result:** Always know what to prioritize tomorrow

---

## Two Classes of RAG Improvements

### Class 1: Extract More Metadata
**Process:** Text chunks → Structured data → Enhanced search

**Examples:**
- **Finance:** Fiscal vs calendar years, contract status
- **Legal:** Signed/unsigned contracts, payment terms
- **Research:** Call types (interview, standup, design review)

### Class 2: Generate Synthetic Text
**Process:** Structured/unstructured data → Optimized summaries → Enhanced embeddings

**Examples:**
- **Images:** Detailed descriptions for semantic search
- **Documents:** FAQ extraction, contextual summaries
- **Tables:** Natural language descriptions of data

---

## Approach 1: Structured Data Extraction

**Goal:** Extract metadata to enable structured querying

```python
class FinancialStatement(BaseModel):
    revenue: float
    net_income: float
    earnings_per_share: float
    operating_expenses: Optional[float] = None
    cash_flow: Optional[float] = None

# Extract and store in searchable database
financial_data = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "system", 
        "content": "Extract financial data from earnings report"
    }],
    response_model=FinancialStatement
)
```

**Result:** Query structured database instead of text chunks

---

## Approach 2: Synthetic Text Generation  

**Goal:** Create summaries optimized for recall

```python
class DocumentSummary(BaseModel):
    title: str
    category: str  # Classification
    summary: str   # Optimized for embedding
    entities: List[str]
    
# Generate synthetic text chunk
summary = extract_summary(document)
embedded_summary = embed(summary.summary)

# Use summary as pointer to original
search_results = vector_search(query_embedding, embedded_summaries)
original_docs = [get_original(result.doc_id) for result in search_results]
```

---

## Key Insight: Materialized Views with AI

**What we're really building:**

> "AI-processed materialized views of your data - either through structuring or rewriting"

**Two Paths:**
1. **Structure:** Raw text → Extracted data → Database queries
2. **Rewrite:** Raw content → Optimized summaries → Vector search

**Both approaches:** Transform data into more searchable formats using AI

**Key Insight:** This is the most important concept to remember from today's session
- You're not just building search indices
- You're creating AI-enhanced views of your existing data
- Either by extracting structure or by rewriting for better recall

---

## Metrics: Same Principles, New Applications

**Global Index (Session 1):** Choose best text chunk from single search
**Local Indices (Today):** Choose best search method from multiple options

**Precision & Recall Applied to Tool Selection:**
- **High Recall:** Hit the right index when needed
- **High Precision:** Don't hit irrelevant indices

**Example Questions:**
- Image query triggers image search tool? ✓
- SQL question routes to text-to-SQL tool? ✓

---

## Document Processing Strategies

**Modern Document Handling:**

### PDF Processing
- **Docling:** Free, high-accuracy extraction
- **Gemini/Claude:** Direct PDF processing
- **Focus:** Citation locations, bounding boxes

### Chunking + Metadata
```python
chunks = chunk_document(doc, size=800, overlap=50)
for chunk in chunks:
    chunk.metadata = {
        "document_type": classify_type(chunk),
        "entities": extract_entities(chunk),
        "category": categorize(chunk)
    }
```

### Contextual Retrieval
- Rewrite chunks with surrounding context
- Leverage prompt caching for efficiency

---

## Image Search: Beyond Basic Captions

**The Problem:** Visual language models trained on captioning data

**Challenge:** Generic captions vs. specific user queries

### Bad Prompt
```
"What's in this image?"
→ "Two people"
```

### Better Prompt
```
"Describe this image for search purposes. Include:
- Scene details and mood
- People and their actions  
- Objects and their relationships
- Potential user questions this answers"
→ "Two people arguing intensely at dinner table, one holding knife, mysterious foggy atmosphere"
```

---

## Advanced Image Processing

**Enhance Context with Multiple Signals:**

```python
def process_image(image_path, document_context=None):
    # Extract OCR text
    ocr_text = extract_ocr(image_path)
    
    # Get surrounding text if in document
    context = get_surrounding_text(image_path, document_context)
    
    # Generate detailed description
    description = generate_description(
        image=image_path,
        ocr_text=ocr_text,
        context=context,
        user_query_examples=SAMPLE_QUERIES
    )
    
    return {
        "description": description,
        "ocr_text": ocr_text,
        "bounding_boxes": extract_bounding_boxes(image_path)
    }
```

---

## Image Description Prompt Example

```python
PROMPT = """
Analyze this image with the following context:
- OCR Text: {ocr_text}
- Surrounding document text: {context}

Provide:
1. Visual description of the scene
2. Technical details (chart type, data shown, etc.)
3. Key entities and relationships
4. Potential search queries this would answer
5. Summary optimized for embedding

Generate 2-3 potential questions users might ask about this image.
"""
```

**Goal:** Bridge the gap between user queries and image embeddings

---

## Testing Synthetic Data Quality

**Remember:** Synthetic data must improve metrics, not just look good

### Evaluation Process
1. **Generate synthetic queries** for your data types
2. **Measure recall** before and after enhancement  
3. **Compare approaches** (structured vs summary)
4. **Iterate on prompts** based on performance

```python
# Test recall improvement
baseline_recall = test_retrieval(queries, original_chunks)
enhanced_recall = test_retrieval(queries, enhanced_chunks)

assert enhanced_recall > baseline_recall
```

---

## Performance Debugging Framework

**When System Fails, Ask:**

1. **Traffic Issues:**
   - Does this segment get enough/too much traffic?
   - Should we promote/demote this capability?

2. **Tool Selection Issues:**  
   - Are we choosing the right tool for queries?
   - Need better routing prompts/examples?

3. **Retrieval Issues:**
   - Given correct tool, finding right answer?
   - Need better embeddings/filtering?

**Systematic Approach:** Just numbers multiplied together
- Find the lowest number in your probability chain
- Improve that specific component
- Re-measure and repeat

**Result:** Always know what to improve next

**Reality Check:** After doing this for a while, it becomes very boring
- All the work is collecting these data points
- But you'll always know what to do tomorrow
- Simple numbers multiplied together - find the lowest and improve it
- **Why simple metrics matter:** LLMs across the whole process won't tell you what to fix

---

## Organizational Benefits

**Team Structure for Multiple Indices:**

### Frontend/Interface Team
- Tool segmentation and design
- User experience optimization
- A/B testing different approaches

### Backend/Implementation Teams  
- **Document Team:** PDF processing, chunking
- **Image Team:** Vision models, OCR, descriptions  
- **Structured Data Team:** Text-to-SQL, extractions

### Integration/Routing Team
- Tool orchestration and routing
- Performance monitoring
- Cross-system optimization

## SQL Generation: Beyond Simple Queries

**The Business Reality:** Multiple correct answers, complex schemas

### Reframe Using Our Tools
1. **Inventory:** Do we have right tables? Right columns? Can we retrieve them?
2. **Capabilities:** Can we demonstrate understanding from historical queries?
3. **Business Logic:** Revenue isn't always just SUM(sales)

### Example: "Month over Month Revenue"
**The Problem:** What does this actually mean?
```sql
-- Option 1: 30-day rolling window
SELECT * FROM revenue WHERE date >= CURRENT_DATE - INTERVAL 30 DAY

-- Option 2: Calendar month
SELECT * FROM revenue WHERE MONTH(date) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH)

-- Option 3: 28-day rolling average
SELECT AVG(revenue) FROM revenue WHERE date >= CURRENT_DATE - INTERVAL 28 DAY
```

**Solution:** Golden SQL snippets that capture business definitions
- Create UI to let users "star" correct SQL statements
- Build inventory of business-specific calculation patterns
- Use these as few-shot examples

---

## Table Retrieval Strategy

### Step 1: Table Discovery
```python
# Test: "How many users generated $10k+ revenue?"
# Should retrieve: users_table + finance_table
expected_tables = ["users", "finance"]
retrieved_tables = table_retriever(query)
assert all(table in retrieved_tables for table in expected_tables)
```

### Step 2: SQL Snippet Retrieval
```python
# Test: "Show month over month growth"
# Should retrieve: business-specific MoM calculation
expected_snippets = ["month_over_month_revenue"]
retrieved_snippets = snippet_retriever(query)
assert relevant_snippet in retrieved_snippets
```

### Step 3: Co-occurrence Patterns
- Track which tables are used together
- If queries use users + finance, maybe also include orders
- Trade-off between precision and recall

---

## The Recursive Playbook Pattern

**Universal Application:**
- **Documents:** Extract → Structure → Query
- **Images:** Describe → Embed → Retrieve  
- **Tables:** Discover → Pattern → Execute
- **Text-to-SQL:** Inventory + Capabilities framework

**Key Insight:** Same playbook recursively applies to every subsystem
1. Define synthetic data and evals
2. Measure precision/recall (proxy for success probability)
3. Segment to identify problems
4. Split monolithic retriever into specialized ones
5. Improve each retriever individually

**Reality:** None of these systems are "fire and forget"
- Continuous monitoring required
- Always iterating on processes
- You're responsible for retrieval, no matter how good AI gets

---

## Session 5 Homework

**Apply These Concepts:**

1. **Identify Your Segments:** What specific search needs exist?
2. **Choose Your Approach:** Structured extraction or synthetic summaries?
3. **Build One Index:** Pick highest-impact segment, implement solution
4. **Measure Performance:** Before/after recall metrics
5. **Plan Integration:** How will this connect to routing system?

**Key Questions:**
- What metadata exists that could make search simpler?
- Should you extract structured data or generate synthetic summaries?
- What business-specific logic needs to be captured in examples?
- Where are you applying the recursive playbook pattern?

**Challenge:** Try to identify whether your problem is inventory (missing data) or capabilities (missing examples)

---

## Next Session Preview: Apply

**Session 6: Function Calling Done Right**

- Combine multiple indices into unified system
- Query routing strategies and evaluation
- Human-AI collaboration patterns
- UI considerations for multi-tool systems
- Complete RAG improvement methodology

**Goal:** Transform individual tools into cohesive application

**Pattern Recognition:** This is how machine learning evolves
1. **Start:** Small specialized models
2. **Scale:** Bigger monolithic models
3. **Specialize:** Mixture of experts when can't scale further
4. **Consolidate:** Eventually bigger monolithic model again

**Next week:** Build mixture of retrievers, combine with router

---

## Key Takeaways

### Technical Insights
1. **Local beats global** when segments exist
2. **Two improvement classes:** Extract structure or generate summaries
3. **AI-powered materialized views** of your data
4. **Metrics transfer:** Precision/recall apply to tool selection

### Strategic Insights  
1. **Divide and conquer:** Teams can work on separate indices
2. **Systematic debugging:** Formula tells you what to fix
3. **User-driven design:** Optimize for actual search patterns
4. **Data quality matters:** Synthetic data must improve metrics
5. **Boring is good:** Repetitive process means you know what to do next
6. **Recursive patterns:** Same playbook applies to every specialized component

---

## Remember the Fundamentals

**Technology Changes, Principles Endure:**

- **Measure first:** Establish baselines before optimizing
- **Segment users:** Different needs require different solutions  
- **Iterate systematically:** Data-driven improvement cycles
- **Focus on impact:** Work on what matters most

**Next week:** Bring it all together with intelligent routing

---

## Thank You

**Questions for office hours:**
- Which approach fits your use case better?
- How to measure success for your specific domain?
- Team organization for multiple indices?

*maven.com/applied-llms/rag-playbook*