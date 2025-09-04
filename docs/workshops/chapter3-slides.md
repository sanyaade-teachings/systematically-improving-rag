# Chapter 3 Slides

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

**Session 3:** The Art of RAG UX: Turning Design into Data

Jason Liu

---

## Today's Goals

**From Synthetic Data to Real User Feedback**

- Design systems that collect high-quality user feedback
- Master streaming techniques for better user experience
- Learn prompting and Chain of Thought best practices
- Turn every user interaction into training data
- Bridge the gap between synthetic and real-world data

**Focus: Small UX changes = 5-10x more feedback**

---

## Course Context: Building the Data Flywheel

### Sessions 1-2: Foundation
- **Session 1:** Synthetic data and evaluations (faking it)
- **Session 2:** Fine-tuning on synthetic data (making it)

### Session 3: The Bridge ← Today
- **Goal:** Collect real user data to supplement synthetic work
- **Challenge:** How to get users to give us quality feedback
- **Opportunity:** Design choices that 5-10x feedback volume

### Sessions 4-6: Data-Driven Optimization
- Use real feedback for segmentation and improvement

---

## The Feedback Collection Hierarchy

**Most Important:** Looking at your input data  
**Second Most Important:** Getting user feedback

**The Problem:** Most systems collect terrible feedback
- Vague thumbs up/down with no context
- Hidden or hard-to-find feedback buttons
- No follow-up questions to understand failures
- Feedback that doesn't correlate with actual problems

**The Opportunity:** Small design changes → massive data improvements

---

## Bad vs Good Feedback Design

### Bad Design: Subtle and Generic
```
[Answer displayed]

                    👍  👎
                 (tiny buttons, bottom right)
```

### Good Design: Prominent and Specific
```
[Answer displayed]

Did we answer your question today?
┌─────────────────┬─────────────────┐
│     👍 YES      │      👎 NO      │
│   (large btn)   │   (large btn)   │
└─────────────────┴─────────────────┘
```

**Result:** 5x more feedback with better design

---

## The Power of Specific Copy

### Generic (Useless)
```
👍 Good    👎 Bad
```
**Problem:** "Bad" could mean slow, wrong, too long, confusing, etc.

### Specific (Actionable)  
```
Did we successfully complete your task?
┌─────────────────────────────────────┐
│            👍 YES, DONE             │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│         👎 NO, DIDN'T HELP          │
└─────────────────────────────────────┘
```

**Benefits:** 
- Clear success criteria alignment
- Actionable labels for data analysis
- Better correlation with business outcomes

---

## Follow-Up Questions for Rich Data

### When User Says "No"
```
Why wasn't your question answered?

□ Too slow
□ Called wrong functions  
□ Bad response format
□ Misinterpreted my request
□ Missing information
□ Other: ___________
```

**Impact:**
- Segment failure modes
- Identify specific improvement areas
- Create targeted evaluation datasets
- Debug system bottlenecks systematically

---

## Enterprise Feedback: The Slack Integration

### Consumer Pattern
- Small feedback buttons
- Passive collection
- Volume-based insights

### Enterprise Pattern
- **Direct Slack integration:** Negative feedback → Customer success channel
- **Human review:** Manual assessment of each failure
- **Eval integration:** Add examples to test suites
- **Customer loop:** Report back on improvements in meetings
- **Critical:** Let customers know their feedback will improve the product
- **Behavior:** Customers need to see feedback leads to action

**Result:** 5x more feedback + stronger customer relationships
- **Speed:** Fine-tune 5x faster with more data
- **Trust:** Build trust while collecting data and building evals

---

## Mining Hard Negatives Through UX

**The Challenge:** Finding good negative examples for fine-tuning

### Traditional Approach
```
Anchor: "How to deploy?"
Positive: deployment_guide.md
Negative: ??? (random documents)
```

### UX-Driven Approach: Citation Deletion
```
[Generated Answer with Citations]
📄 deployment_guide.md    [×] Delete
📄 security_setup.md     [×] Delete  
📄 api_reference.md      [×] Delete

When user deletes → Hard negative example!
```

**Benefit:** User-validated irrelevant content = perfect training data

---

## Facebook-Style Feedback Collection

### Infinite Scroll Pattern
```
People You May Know:
┌─────────────────┬─────────────────┐
│  User 1  [Add]  │  User 2  [Add]  │
└─────────────────┴─────────────────┘
┌─────────────────┬─────────────────┐
│  User 3  [Add]  │  User 4  [Add]  │  
└─────────────────┴─────────────────┘
                  ...
```

### Limited Options Pattern  
```
Top 5 Suggestions:
┌─────────────────────────────────────┐
│  User A  [Add]              [Skip]  │
│  User B  [Add]              [Skip]  │
│  User C  [Add]              [Skip]  │
└─────────────────────────────────────┘
```

**RAG Application:** Show top documents, let users add/remove = training data

---

## The Dating App Secret

**Why Tinder/Hinge Have Great Models:**

1. **High Volume:** Millions of interactions daily
2. **Clear Positive/Negative:** Swipe right/left  
3. **Simple Objective:** Match prediction
4. **Continuous Feedback:** Every interaction is a label

**RAG Lesson:** Design interactions that naturally generate training labels

**Examples:**
- Citation deletion = negative examples
- Follow-up clicks = positive examples  
- Query refinement = preference learning

---

## Citations: Trust + Training Data

### Why Citations Matter
- **User Trust:** "Where did this come from?"
- **Verification:** Users can check sources
- **Training Data:** Click patterns = relevance signals
- **Customer Questions:** "How does AI get this info?" "How do I know it's accurate?"
- **Beat them to the punch:** Include citations proactively
- **Preview functionality:** Show what data is being used

### Simple Citation Implementation
```python
class Response(BaseModel):
    content: str
    citations: List[Citation]

class Citation(BaseModel):
    text: str
    source_id: str
    title: str
```

### Advanced: Bounding Box Citations
```python
class BoundingBoxCitation(BaseModel):
    text: str
    pdf_path: str
    page_number: int
    bbox: List[float]  # [x1, y1, x2, y2]
```

**Recent Innovation:** Cite bounding boxes of parsed data
- **Beyond text chunks:** Cite actual PDF locations
- **Visual citations:** Show boxes over original document
- **High fidelity:** Reference specific tables, titles, sections
- **Better trust:** Users see exact source location

---

## Streaming: The Table Stakes Feature

**Reality Check:** Only 20% of companies implement streaming well

### Why Streaming Matters
- **User Expectation:** Instant response feeling
- **Perceived Performance:** 11% faster with animated progress (same wait time!)
- **Retention:** Users tolerate 8 seconds with visual feedback vs instant abandonment
- **Abandonment:** Reduces dropout rates significantly
- **Trust:** Applications with engaging loading screens report higher satisfaction
- **Real Examples:** Facebook's skeleton screens reduced perceived load times

### What to Stream
1. **Response Text:** Token by token
2. **Tool Calls:** Show function execution  
3. **Interstitials:** "Searching documents...", "Analyzing results..."
4. **UI Components:** Citations, follow-ups as they're ready

---

## Streaming Implementation Strategy

### The Migration Problem
> "Migrating from non-streaming to streaming is a pain in the ass"

**Recommendation:** Build streaming from day one
- **Reality:** Will take weeks out of your dev cycle to upgrade later
- **Streaming is table stakes:** Users expect it in LLM applications
- **Build it now:** Much easier than retrofitting later

### Technical Approach
```python
@app.route('/chat', methods=['POST'])
def chat_stream():
    def generate():
        # Stream interstitials
        yield f"data: {json.dumps({'type': 'status', 'message': 'Searching...'})}\n\n"
        
        # Stream tool calls
        for tool_result in execute_tools():
            yield f"data: {json.dumps({'type': 'tool', 'data': tool_result})}\n\n"
        
        # Stream response
        for token in llm_stream():
            yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"
    
    return Response(generate(), mimetype='text/plain')
```

---

## Structured Streaming with Citations

### Traditional Response
```json
{
  "answer": "The deployment process involves three steps...",
  "done": true
}
```

### Structured Streaming Response
```python
class StreamingResponse(BaseModel):
    content: str = ""
    citations: List[Citation] = []
    follow_ups: List[str] = []
    status: str = "generating"

# Stream updates to each field
for update in llm_stream():
    response.content += update.token
    if update.citation:
        response.citations.append(update.citation)
    yield response.model_dump()
```

**Advanced Pattern:** Stream different UI components separately
- **Content:** Streams token by token
- **Citations:** Added as they're identified
- **Follow-ups:** Generated and streamed at the end
- **Status:** Updates throughout the process

**Result:** Users see progress on multiple fronts, better perceived performance

---

## Slack Bot Feedback Patterns

### Basic Acknowledgment
```
User: "How do I deploy the app?"
Bot: 👀 (eyes reaction - received)
     
     [Processing...]
     
     ✅ (checkmark - completed)
     Response: "To deploy the app..."
```

### Pre-seeded Feedback
```
Bot Response: "To deploy the app, run..."

👍 👎 ⭐ (auto-added reactions)
```

**Impact:** Pre-seeded reactions dramatically increase feedback rates

**Key Insight:** If reactions aren't there, users won't think to give feedback
- **Behavioral psychology:** Prompt the action you want
- **"How did I do?"** + pre-seeded reactions = 5-10x more feedback
- **Simple implementation:** Auto-add emoji reactions to responses

**Data Collection:** Track reaction patterns for continuous improvement
- **Cache:** Save question-answer pairs as few-shot examples
- **Analytics:** Monitor which responses get what reactions

---

## Prompting the User, Not Just the AI

**Insight:** People are lazy and don't know what they want

### Bad Approach
```
[Empty text box]
"What would you like to know?"
```

### Good Approach  
```
Try asking:
• "How do I deploy to production?"
• "What are the security requirements?"
• "Show me the API documentation"
• "Help me troubleshoot connection issues"
```

**Benefits:**
- Shows capabilities users didn't know existed
- Reduces empty/vague queries
- Generates higher-quality training data
- **Key insight:** People are lazy and don't know what they want
- **Discovery:** Show features users wouldn't have thought about
- **Session 4 preview:** Discover these through conversation data analysis

---

## Chain of Thought: The Hidden Performance Booster

**Reality:** Massively underutilized by most teams

### Performance Impact
- **10% improvement** in most tasks
- **Make or break** difference for production deployment
- **Loading interstitial** opportunity with streaming
- **Game changer:** With O1/R1 models, reasoning becomes visible
- **Multiple purposes:** Better reasoning + loading indicator

### Modern Implementation
```python
# With O1/R1 models
response = client.chat.completions.create(
    model="o1-preview",
    messages=[{"role": "user", "content": prompt}]
)

# Stream the reasoning
for chunk in response:
    if chunk.type == "reasoning":
        yield {"type": "thinking", "content": chunk.content}
    elif chunk.type == "response":  
        yield {"type": "answer", "content": chunk.content}
```

---

## Chain of Thought for Complex Tasks

### Use Case: SaaS Pricing Quotes
```
Context: 15-page pricing document + 1-hour transcript
Goal: Generate pricing proposal email

Chain of Thought Prompt:
1. "First, reiterate the key pricing variables from our document"
2. "Next, identify parts of transcript that mention pricing"  
3. "Then, find relevant sections of pricing document"
4. "Finally, reason through the appropriate pricing options"
```

### Results
- **90% acceptance rate** for generated quotes
- **Single prompt** replaces complex multi-agent system
- **Easy verification** with structured reasoning
- **Rich training data** from sales rep feedback

---

## The Long Context + Chain of Thought Pattern

### Traditional RAG Approach
```
Query → Retrieve chunks → Stuff context → Generate
```

### Long Context + CoT Approach  
```python
system_prompt = f"""
Context: {full_pricing_document}

For each query:
1. Reiterate relevant pricing variables
2. Extract pricing mentions from transcript  
3. Reference applicable document sections
4. Reason through recommendation
"""

user_prompt = f"""
Transcript: {full_transcript}
Generate pricing proposal email.
"""
```

**Benefits:** Better reasoning, verifiable citations, simpler architecture

---

## Validation: The Hidden Quality Multiplier

**The Problem:** Single-step generation isn't enough for high-quality answers

### Validation Pattern
```python
class EmailResponse(BaseModel):
    subject: str
    body: str
    
    @validator('body')
    def validate_urls(cls, v):
        urls = extract_urls(v)
        for url in urls:
            if not is_allowed_domain(url):
                raise ValueError(f"Invalid URL domain: {url}")
            if not url_exists(url):  # GET request check
                raise ValueError(f"URL not found: {url}")
        return v
```

### Real Results
- **Before validation:** 4% failure rate (invalid URLs)
- **After validation:** 0% failure rate with retry loop
- **After fine-tuning:** Validators never triggered again
- **Implementation time:** 3 days to build

**Key Insight:** Validators become evals in production, improving both user experience and model training

---

## UI Components That Collect Data

### Follow-Up Questions
```
[Generated Response]

Continue with:
• "Tell me more about deployment"
• "What about security considerations?"  
• "Show me code examples"
```
**Data:** Track click patterns → improve suggestions

### Source Interaction
```
[Response with hoverable citations]
📄 deployment.md ← Click to preview
📄 security.md   ← Click to preview
```
**Data:** Preview clicks = relevance signals

### Share/Save Buttons
```
[Response] 
├── 📋 Copy   ← Usage signal
├── ⭐ Save   ← High quality signal  
└── 🔗 Share  ← Validation signal
```

---

## Data Collection Everywhere

**Once you start looking, you'll see feedback opportunities everywhere:**

### Perplexity Patterns
- Related questions
- Source hover interactions
- Follow-up suggestions
- Share/copy behaviors

### ChatGPT Patterns  
- Regeneration requests
- Edit suggestions
- Conversation ratings
- Feature usage tracking

**Exercise:** Audit your favorite AI tools for data collection patterns

### The Universal Truth
**Once you start looking for feedback collection, you'll see it everywhere:**
- Perplexity: Related questions, source hovers, follow-up suggestions
- ChatGPT: Regeneration, edit suggestions, conversation ratings
- Every tool: Multiple touchpoints for data collection

**Your mission:** Identify 5 feedback opportunities in your current application

---

## This Week's Implementation Checklist

### Immediate (Day 1)
1. **Redesign feedback buttons:** Make them large and specific
2. **Add follow-up questions:** When users give negative feedback  
3. **Implement basic streaming:** At minimum, token-by-token response

### Short-term (This Week)
1. **Add citations:** Basic markdown links to sources
2. **Create suggestion prompts:** Show example queries
3. **Set up feedback logging:** Store all user interactions

### Medium-term (Next Month)
1. **Slack/webhook integration:** Route feedback to team channels
2. **Citation deletion UI:** Let users remove irrelevant sources  
3. **Chain of Thought streaming:** Show reasoning process

---

## Next Week Preview: Data Analysis

**Session 4 Focus:**
- Analyze all the feedback you've collected
- Segment users and queries to find patterns
- Identify high-impact improvement opportunities  
- Build data-driven product roadmaps

**Connection:** This week's UX improvements become next week's analysis dataset

---

## Key Takeaways

### Design Insights
1. **Small changes, big impact** - 5-10x feedback improvement possible
2. **Specific > Generic** - "Did we complete your task?" vs "Good/Bad"
3. **Streaming is table stakes** - Build it from day one
4. **Every interaction is data** - Design for continuous learning

### Technical Insights  
1. **Chain of Thought works** - 10% performance improvement
2. **Citations build trust** - And provide training signals
3. **Structured streaming** - Better UX + richer data collection
4. **Long context + CoT** - Often beats complex RAG systems

### Strategic Insights
1. **Feedback design = competitive advantage** - Most teams do this poorly
2. **User prompting matters** - Show capabilities proactively  
3. **Enterprise needs human touch** - Slack integrations build relationships
4. **Data compounds** - Today's UX decisions become tomorrow's models

---

## Remember: Every User Interaction is an Opportunity

**The Flywheel:**
- Better UX → More feedback → Better training data → Better models → Better UX

**Your Goal:** Turn every user session into multiple training examples

**Success Metric:** 5-10x increase in useful feedback volume within 2 weeks

**Reality Check:** Most teams collect terrible feedback because:
- Buttons are too small and hidden
- Copy is vague ("good/bad" tells you nothing)
- No follow-up questions to understand failures
- Users don't know their feedback matters

**The Fix:** Small design changes = massive data improvements

---

## Thank You

**Questions for office hours:**
- How to implement streaming in your tech stack?
- Best feedback patterns for your specific use case?
- Chain of Thought prompting strategies?
- Citation implementation approaches?

**Next week:** Analyzing all that beautiful data you'll collect

*maven.com/applied-llms/rag-playbook*