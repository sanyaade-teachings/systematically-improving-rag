# Chapter 6 Slides

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

**Session 6:** Apply: Function Calling Done Right

Jason Liu

---

## Today's Goals

**Combining Search Indices into a Cohesive Application**

- Query routing vs. retrieval indices
- Query routing main challenges and solutions  
- Testing and evaluation strategies
- UI considerations for human-AI interaction
- Food for thought and practical applications

**Move from individual search indices to unified system**

---

## Building on Previous Sessions

**Sessions 4-5: Individual Search Indices**
- Documents, images, text-to-SQL
- Two improvement strategies:
  1. **Structured Data Extraction**
  2. **Text Summaries for Search**

**Today: Combination Strategy**
- Intelligent query routing
- Parallel tool calling
- Human-AI collaboration

---

## Case Study: Blueprint Search

**Scenario:** Construction company searches blueprint images

### Step 1: Extract into Index
- Blueprint extractor (OCR → description + date)
- Structured database storage
- Searchable fields

### Step 2: Define Search Tool
```python
class SearchBlueprint(BaseModel):
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
```

---

## You Are a Framework Developer

**Key Insight:** Retrieval methods = REST API methods

**Why this matters:**
- **Modularity:** Multiple APIs query same DB differently
- **Team Scalability:** Individual teams per API type
- **Clean Boundaries:** Interface, implementation, routing

> "You are effectively a framework developer for the language model"

---

## Three-Layer Architecture

### 1. Interface Layer
```python
class SearchText(BaseModel):
    search_query: str
    filter_by_type: Literal["contracts", "proposals", "bids", "all"]
```

### 2. Implementation Layer  
```python
async def execute(self):
    q = table.search(query=self.search_query)
    if self.filter_by_type != "all":
        q = q.filter(type=self.filter_by_type)
    return q.select(["title", "description"]).to_list()
```

### 3. Gateway Layer
```python
tools = [SearchBlueprint, SearchText, AnswerQuery]
# Route → Execute → Synthesize
```

---

## Team Organization Benefits

**Interface Team**
- Tool segmentation and design
- A/B testing configurations

**Implementation Team**  
- Per-tool performance optimization
- Better embeddings, ranking models

**Gateway Team**
- Tool routing and orchestration
- Prompt engineering, model selection

---

## Parallel Tool Calling

**Why parallel tools are powerful:**
- **Speed:** Concurrent searches
- **Comprehensiveness:** Blueprint + text simultaneously  
- **Composability:** Search + clarification + answers

```python
class ToolSuite(BaseModel):
    search_blueprints: Optional[SearchBlueprint]
    search_text: Optional[SearchText]  
    clarify_question: Optional[ClarifyQuestion]
    answer_with_citations: Optional[AnswerQuery]
```

---

## The Systematic Approach

**Same process, applied again:**

### Step 1: Create Test Dataset
```python
example_queries = [
    ("Find blueprints for city hall from 2010", ["search_blueprints"]),
    ("Show me contract proposals", ["search_text"]),  
]
```

### Step 2: Focus on Recall Metrics
- **Data is crucial** for tool evaluation
- **Precision matters later** (avoid wasted compute)
- **Synthetic data generation** requires good descriptions

---

## Dynamic Few-Shot Examples

### V0: Hard-coded Examples
```python
# 10-40 examples per tool
search_blueprint_examples = [
    "Find city hall blueprints from 2010 → SearchBlueprint(...)",
    "Show school building plans from 2015 → SearchBlueprint(...)"
]
```

### Advanced: Search-Based Retrieval
1. **Build Example Database:** Query → tool mappings
2. **Runtime Retrieval:** Find relevant historical examples  
3. **Dynamic Prompting:** Inject examples into prompt
4. **Continuous Improvement:** More users = better examples

---

## The Complete RAG Improvement System

### 1. Synthetic Data Flywheel
Generate query-to-tool datasets for evaluation

### 2. Establish Recall Metrics  
Per-tool evaluation, system-wide metrics

### 3. Iterate on Few-Shot Examples
Static → Dynamic, 10-40 examples per tool

### 4. Build Example Search System
Store successful mappings, retrieve optimal examples

**Key:** Don't be surprised by 10-40 examples per tool!

---

## Challenge 1: Low Per-Class Recall

**Problem:** 65% overall recall masks individual tool failures

| Expected Tools | Predicted | Issue |
|---|---|---|
| [search_text; search_blueprints] | [search_text] | Missing blueprints |
| [search_blueprints] | [search_text] | Wrong tool |

**Root Cause:** `search_blueprints` has 0% recall!

**Solutions:**
- Better tool descriptions
- Targeted few-shot examples  
- Address class imbalance

---

## Challenge 2: Tool Confusion Matrix

| | Predicted: blueprints | Predicted: text |
|---|---|---|
| **Actual: blueprints** | 5 | 4 |  
| **Actual: text** | 0 | 9 |

**Blueprint queries misclassified as text search**

**Systematic Debugging:**
1. Filter for failures
2. Pattern analysis
3. Delineation examples
4. Positive/negative examples
5. Edge case coverage

---

## Warning: Data Leakage Prevention

**Critical Issue:** Test examples in few-shot prompts

**Why this happens:**
- Limited data (dozens of examples)
- Overlap between train/test
- Synthetic data similarity

**Consequences:**
- Overestimated performance
- Users see few-shot examples as answers
- Production failures

**Prevention:** Strict train/test splits

---

## Understanding System Performance

### The Core Equation
```
P(Correct chunk found) = P(Correct chunk | correct retriever) × P(correct retriever)
```

**Sessions 4-5:** Individual tool performance
**Session 6:** Router/gateway performance

**This identifies your limiting factor:**
- Router problem → Better prompts, examples
- Retriever problem → Better embeddings, filtering

---

## Extended Performance Formula

```
P(success) = P(correct tool | query) × P(success | correct tool) × P(query)
```

| Component | Represents | Improve With |
|---|---|---|
| P(query) | UI Design & Education | Better UX, training |
| P(success) | Overall App Quality | Satisfaction, reliability |
| P(success \| correct tool) | Retrieval Quality | Embeddings, ranking |  
| P(correct tool \| query) | Router Quality | Prompts, examples |

**Strategic:** Segmentation analysis → research vs product roadmap

---

## UI Design Philosophy

**Don't Force Chat When Tools Are Better**

**Examples of specialized interfaces:**
- **YouTube:** Video search index
- **Google Maps:** Directions index  
- **LinkedIn:** Professional network
- **Google:** Everything else

> "When I want directions, I open Maps. For videos, YouTube. Don't force users to 'chat with x'"

---

## JSON Schema → Form Generation

**Technical Implementation:**
- Each tool = JSON schema
- Auto-generate forms for humans
- Users review/correct parameters
- Enable AI + human access

**The P(query) Factor:**
- Expert users → P(correct tool) = 100%
- Why delegate to AI?
- Offer chat AND structured search

---

## Human-AI Training Loop

**User interactions become training data:**
- **Click-through data:** Which results selected?
- **Correction patterns:** When do users modify AI choices?
- **Usage analytics:** Tool effectiveness

**Result:** Human feedback improves ranking and routing

**Design Principle:** Build for both humans and AI

---

## Food for Thought

**Apply at work:**

### From Previous Sessions
- Generate synthetic data
- Topic modeling analysis
- User feedback mechanisms
- Entity-specific indices

### Query Routing Focus
1. Which search methods would you want?
2. Should tools be exposed to users?  
3. Can tools run in parallel?
4. How do users discover capabilities?

---

## Course Overview

### Sessions 4-5: Individual Indices
- Segmentation & topic modeling
- Specialized retrieval (docs, images, SQL)
- Query routing foundation

### Session 6: Combining Everything
- Tool architecture layers
- Query routing metrics
- RAG playbook applied to routing
- Human-AI collaboration

**Core Theme:** Same systematic process, different levels

---

## Course Conclusion

### What You Must Internalize

**1. Evaluations Are Everything**
> "Evaluations are what you need to understand how to improve"

- Evaluations are datasets that inform decisions
- Power few-shot examples  
- Enable retrieval systems
- Become fine-tuning data

**Too many teams have 10-20 examples. Insufficient.**

---

## Data Is the Foundation

**Synthetic data + customer feedback = same coin**
- All data augmentation at different scales
- Fundamental building blocks of ML products  
- Same process for 20+ years in ML

> "If you refuse to believe this, you're condemning yourself to being lost and confused in this hyped landscape"

---

## The Virtuous Cycle

```
Good Product (strong UX) 
    → Better Evaluations  
    → Better Models/Training
    → Even Better Product
    → Repeat...
```

**Data analysis over evaluation segments** → focus development

---

## Technology Changes, Fundamentals Endure

**Constants that matter:**
- **Strong fundamentals** over hype
- **Product-oriented thinking** over tech chasing  
- **Data-driven improvement** over intuition
- **Systematic evaluation** over ad-hoc testing

**What's new becomes old:**
- New companies, technologies, frameworks
- Same underlying principles
- Focus on transcendent fundamentals

---

## Thank You & Feedback

**Course Goal:** 
Convey importance of strong fundamentals for successful RAG

**Your Feedback:**
- Missing topics?
- Improvement suggestions?
- Better examples?

**Continuing Support:**
- Office hours all year
- Slack community
- Additional videos based on feedback

**Remember:** Technology changes, fundamentals endure

---

## Course Complete

**Next:** Office hours, Q&A, community support

*maven.com/applied-llms/rag-playbook*