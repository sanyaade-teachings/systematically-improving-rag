# Chapter 6 Slides: Function Calling Done Right

*Session 6 of Systematically Improving RAG Applications*

**Jason Liu (@jxnlco) - jxnl.co**

---

## Session Overview

**Today's Focus: Combining Search Indices into a Cohesive Application**

- **Query routing vs. retrieval indices**
- **Query routing main challenges and solutions** 
- **Testing and evaluation strategies**
- **UI considerations for human-AI interaction**
- **Food for thought and practical applications**
- **Course conclusion and key takeaways**

**Goal:** Move from individual search indices to a unified system that intelligently routes queries to the right tools.

---

## Building on Previous Sessions

**What we've learned so far:**
- Sessions 4-5: Building individual search indices (documents, images, text-to-SQL)
- Two main improvement strategies:
  1. **Structured Data Extraction**: Turn chunk data into structured data
  2. **Text Summaries**: Create comprehensive summaries for full-text/embedding search

**Today:** How to combine these indices into a cohesive application through intelligent query routing.

---

## Case Study: Blueprint Search Index

**Hypothetical scenario:** Construction company needs to search blueprint images

### Step 1: Extract into Index
- **Blueprint Extractor**: Extracts description and date from OCR'd blueprint images
- **Database Storage**: Structured data with searchable fields
- **New Database**: Now we can query blueprints systematically

### Step 2: Define the Search Tool
```python
class SearchBlueprint(BaseModel):
    description: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    
    async def execute(self):
        query = blueprint_table.search(description=self.description)
        if self.start_date:
            query = query.filter(date >= self.start_date)
        if self.end_date:
            query = query.filter(date <= self.end_date)
        return query.to_list()
```

## Core Philosophy: You Are a Framework Developer

**Key Insight:** Each retrieval method should feel like a REST API method, not direct database access.

**Why this matters:**
- **Modularity**: Multiple APIs can query the same database in different ways
- **Team Scalability**: Individual teams can work on specific APIs (emails vs blueprints vs schedules)
- **Separation of Concerns**: Clean boundaries between interface, implementation, and routing

> "You are effectively a framework developer for the language model" - Jason Liu

From experience building microservices for retrieval, this approach scales to larger distributed teams.

---

## The Three-Layer Architecture

### 1. Interface Layer: Defining Tools
**Example: Text Search Tool**
```python
class SearchText(BaseModel):
    search_query: str
    filter_by_type: Literal["contracts", "proposals", "bids", "all"] = "all"
    
    # Tool description and examples go here
```

*Discovered through data analysis and segmentation - contracts, proposals, and bids were the most important filter categories.*

### 2. Implementation Layer: Backend Logic
```python
async def execute(self):
    q = table.search(query=self.search_query)
    if self.filter_by_type != "all":
        q = q.filter(type=self.filter_by_type)
    return q.select(["title", "description"]).to_list()
```

*Database-agnostic: Works with LanceDB, ChromaDB, Turbopuffer, or PostgreSQL*

### 3. Gateway Layer: Router and Orchestration
```python
# System prompt with parallel tool calling
tools = [SearchBlueprint, SearchText, AnswerQuery, ClarifyQuestion]
# Route user query to appropriate tools
# Gather results and synthesize final response
```

## Team Organization Benefits

**How these boundaries help split teams and resources:**

### Interface Team
- **Focus**: Tool segmentation and interface design
- **Tasks**: What tools should exist? What parameters do they need?
- **Experiments**: A/B testing different tool configurations

### Implementation Team  
- **Focus**: Per-tool performance improvement
- **Tasks**: Optimize individual tool recall and precision
- **Experiments**: Better embeddings, filtering, ranking models

### Gateway Team
- **Focus**: Tool routing and orchestration
- **Tasks**: Which tools to call when? How to combine results?
- **Experiments**: Prompt engineering, few-shot examples, model selection

*This mirrors Sessions 4-5 focus on the first two layers.*

---

## Leveraging Parallel Tool Calling

**Why parallel tools are powerful:**
- **Speed**: Multiple searches can run concurrently
- **Comprehensiveness**: Can search blueprints AND text simultaneously
- **Composability**: Tools can include clarification, answer synthesis, and follow-ups

**Complete Tool Suite Example:**
```python
class ToolSuite(BaseModel):
    search_blueprints: Optional[SearchBlueprint] = None
    search_text: Optional[SearchText] = None  
    clarify_question: Optional[ClarifyQuestion] = None
    answer_with_citations: Optional[AnswerQuery] = None
```

**Initial Setup Process:**
1. **Precision/Recall Testing**: Are we calling the right tools?
2. **Continuous Improvement**: Better prompting and argument handling
3. **Available**: LlamaIndex and LangChain have implementations

## The Systematic Approach: Same Process, Applied Again

**Reminder:** This course teaches the same systematic improvement process repeatedly across different RAG components.

### Step 1: Create Test Dataset
```python
# Create query -> expected_tools mapping
example_queries = [
    ("Find blueprints for city hall from 2010", ["search_blueprints"]),
    ("Show me contract proposals", ["search_text"]),  
    ("What are the building plans for 123 Main St built in 2015?", ["search_blueprints"]),
]

for query, expected_tools in example_queries:
    predicted_tools = route_query(query)
    for tool in predicted_tools:
        assert tool.name in expected_tools
```

### Step 2: Focus on Recall Metrics
**Why recall matters more than precision initially:**
- **Data is crucial** for evaluating tool performance
- **Precision matters later** - don't want wasted compute
- **Tool selection** is the limiting factor

**Synthetic Data Generation:** If you have good tool descriptions, you can randomly sample them to create test queries. If you can't generate good synthetic data, your tool descriptions aren't detailed enough.

---

## Dynamic Few-Shot Example System

**Evolution from static to dynamic examples:**

### V0: Hard-coded Examples (10-40 examples per tool)
```python
search_blueprint_examples = [
    "Find blueprints for city hall built in 2010 -> SearchBlueprint(description='city hall', start_date='2010-01-01', end_date='2010-12-31')",
    "Show me school building plans from 2015 -> SearchBlueprint(description='school building', start_date='2015-01-01', end_date='2015-12-31')"
]
```

### Advanced: Search-Based Example Retrieval
Similar to Text2SQL approach:
1. **Build Example Database**: Store successful query -> tool mappings
2. **Runtime Retrieval**: For each user query, find most relevant historical examples
3. **Dynamic Prompting**: Inject retrieved examples into few-shot prompt
4. **Continuous Improvement**: More users = more examples = better performance

**Data Flywheel:** Product generates better evaluations → Better evaluations improve the product → Better product generates even better evaluations

## The Complete RAG Improvement System

**The same systematic process we've used throughout this course:**

### 1. Synthetic Data Flywheel
- **Generate**: Query-to-tool or tool-to-query datasets
- **Purpose**: Create evaluation foundation
- **Scale**: Start with dozens, grow to hundreds/thousands

### 2. Establish Recall Metrics  
- **Per-tool evaluation**: Treat each tool as a classification class
- **System-wide metrics**: Overall routing accuracy
- **Segmentation**: Identify which tools are underperforming

### 3. Iterate on Few-Shot Examples
- **Static Phase**: Hard-code 10-40 examples per tool
- **Dynamic Phase**: Search-based example retrieval
- **Include**: Query → Tool argument mappings
- **Cover**: Individual tools AND tool combinations

### 4. Build Example Search System
- **Database**: Store successful query → tool mappings  
- **Retrieval**: Find optimal examples per user query
- **Similar to**: Summary index, but for query mappings instead of summaries
- **Source**: Initial dataset + production data

**Key Insight:** Don't be surprised if you need 10-40 examples per tool. Prompt caching makes this very tractable, and production systems often use hundreds of examples.

---

# Query Routing Challenges & Solutions

## Challenge 1: Low Per-Class Recall

**Problem:** Overall system recall looks decent (65%), but individual tools are failing

**Root Cause Analysis:**
- **Tool-Level Segmentation**: Treat each tool as a classification class
- **Per-Tool Metrics**: Evaluate recall for each tool individually  
- **Hidden Problems**: System recall can be misleading

**Example Analysis:**

| Expected Tools | Predicted Tools | Correct? | Score | Issue |
|---|---|---|---|---|
| [search_text; search_blueprints] | [search_text] | ❌ No | 1/2 | Missing blueprints |
| [search_text] | [search_text] | ✅ Yes | 1/1 | Perfect |
| [search_blueprints] | [search_text] | ❌ No | 0/1 | Wrong tool |
| [search_text] | [search_text] | ✅ Yes | 1/1 | Perfect |
| [search_text] | [search_text] | ✅ Yes | 1/1 | Perfect |
| [search_blueprints; search_text] | [search_text] | ❌ No | 1/2 | Missing blueprints |

**Key Insight:** 65% overall recall masks the fact that `search_blueprints` has 0% recall!

**Solutions:**
- **Better Tool Descriptions**: More specific, detailed descriptions
- **Targeted Few-Shot Examples**: Focus examples on failing tools
- **Class Imbalance**: Address training data distribution

---

## Tool Confusion

We can build tool confusion matrices to determine which tool is used in place of another

| | Predicted: search_blueprints | Predicted: search_text |
|---|---|---|
| **Actual: search_blueprints** | 5 (TN) | 4 (FP) |
| **Actual: search_text** | 0 (FN) | 9 (TP) |

**How to reduce tool confusion:**
- Look at your data, filter for failures
- Build examples that can help delineate between tools
- Include more positive examples for each tool
- Find examples where the LLM confuses tool A for tool B; give explicit negative examples on when to use each tool
- Look through data and find examples where LLM is confused and explicitly include these in few-shot examples
- In extreme cases, merge tools

---

## Warning on Leakage

Ensure that few-shot prompt examples are not included in the test set!

- How people typically start: dozens of question types with higher than avg performance (depending on how synthetic data is generated)
- Due to limited examples we might overlap examples and tests
- More important to verify in the example retrieval context

---

## Further Testing

### How do we measure the quality of the retrieval subsystem?

| | Session 4, 5 | Session 6 |
|---|---|---|
| **P(Correct chunk found)** | P(Correct chunk found \| correct retriever) | P(correct retriever) |
| | Does a single search method find the correct chunks? | Does the LLM choose the correct search method? |

**Key takeaway:**

This equation can help identify the limiting factor of the system:
- Not using the right retriever (query not routed to the right retriever)
- The retriever itself is bad

**To improve P(correct retriever), continue to experiment on:**
- Precision vs. Recall trade-off
- If precision didn't matter, we can get 100% recall by calling every tool if we don't care about latency
- Examples and prompts for tool selection
- Examples and prompts for arguments
- LLM models used

---

## Interpreting the Formula (Extended)

```
P(success) = P(correct tool selected | query) * P(success | correct tool selected) * P(query)
```

**Where:**
- `P(query)` = UI, Education
- `P(success)` = Quality of application
- `P(success | correct tool selected)` = Retrieval Quality & Generation
- `P(correct tool selected | query)` = Router Quality

---

## UI Considerations

### Thinking about UI

- As we build more tools, each one can be fully specified as a JSON schema, which can be used to model forms
- There are also opportunities to allow either the tool spec to represent forms that the user can review and correct.

### Google Maps Example

*[Examples of Google Maps interface]*

### Build for both Humans and AI

When I want directions, I open maps, if I want videos I visit youtube, don't force users to 'chat with x' when they don't have to

---

## Food for Thought for This Session

### Try this at work or in your own projects

### Work on Food for thought from last few sessions:
- Generate synthetic data to test your system
- Analyze user queries through topic modeling and use this to inform inventory or capabilities issues
- Implement user feedback mechanisms
- Focus on building more robust retrieval indices based on entity types (e.g., documents, images, text-to-SQL)

### Focus on query routing:
- Ask yourself: if you assume your search methods work well, which search methods would you want to work?
- Should any of these tools be explicitly exposed to the user?
- Can our tools be executed in parallel?

### Additional resources:
- https://python.useinstructor.com/examples/search
- https://python.useinstructor.com/examples/planning-tasks/

---

## Overview

### Focus for past two sessions:
- The importance of segmentation and topic modeling, understanding where there may be a lack of inventory vs. lack of capabilities
- Review how to extract and improve each specific type of retrieval index (e.g., documents, images, text-to-SQL)
- Discuss the importance of query routing and how to separate out the query routing step vs. the retrieval index

### Focus for this session:
- Outline tools and example approaches to building a simple query routing and corresponding metrics
- Review how to use the RAG playbook steps (e.g., generate synthetic data, focus on recall-precision metrics) to tackle the query routing sub-problem while improving RAG applications

---

## Course Conclusion

### What I hope to distill into you

- **Evaluations are what you need to understand how to improve.**
  - Evaluations are a dataset that can inform your decisions.
  - They power few-shot examples, which can be used with retrieval to improve performance.
  - They are also the finetuning datasets... (Train vs. Test Split)

- **Synthetic data with large language models and customer feedback from engagement are two sides of the same coin**
  - It's all data and data augmentation.

- **These are the fundamental building blocks of creating successful machine learning products.**
  - If you refuse to believe this, you're condemning yourself to being lost and confused in this hyped landscape.

### The process:
- A good product generates better evaluations (with strong UX)
- Better evaluations allow you to train / finetune models to create an even better product.
- Data analysis over segments of your evaluations tells you where to focus your product development efforts.

**This marks the end of our course.**

Please don't hesitate to give any feedback.

My goal is to convey to folks the importance of having strong fundamentals. If you think there's any way this course can be made better for future iterations, please let me know.

---

*maven.com/applied-llms/rag-playbook*