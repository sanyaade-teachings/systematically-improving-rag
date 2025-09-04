# Chapter 4 Slides

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

**Session 4:** Split: When to Double Down vs When to Fold

Jason Liu

---

## My Favorite Session! 🎯

**Today's Focus:** Data segmentation and strategic decision-making

**Key Questions:**
- How do we segment user data and queries?
- When should we double down on capabilities?
- When should we fold and abandon segments?
- How do we allocate resources effectively?

**This is the actual playbook for post-production analysis**

---

## RAG Flywheel Recap

**Where we've been (Sessions 1-3):**

1. **Initial RAG System** - Basic implementation in place
2. **Synthetic Data Generation** - Create test questions for retrieval evaluation  
3. **Fast Evaluations** - Precision, recall, ranking improvements
4. **User Interaction Data** - Collect feedback through better UI
5. **Fine-Tuning** - Embedding models and rerankers
6. **Production Deployment** - Reasonable product ready to deploy

**Today:** What do we do post-production with lots of data?

---

## Post-Production Data Analysis

**The Challenge:** You have plenty of data coming in - now what?

**Our Approach:**
- **Segmentation and Analysis** - Figure out what's missing and where blind spots are
- **Identify Improvements** - Understand what segments need targeted work
- **Specialized Systems** - Build specific tools for high-value segments  
- **Function Calling Integration** - Combine tools into unified system
- **Query Routing** - Ensure right retriever for each job

**This is where the real value gets unlocked!**

---

## Why Segmentation Matters

### Marketing Example: The 80% Sales Boost

**Scenario:** Consumer product marketing campaign → 80% sales increase

**Without Segmentation:**
- "Sales went up 80%!" 🤷‍♂️
- No actionable insights
- Can't replicate success

**With Segmentation:**
- 60% of increase from **30-45 year old women in Midwest**
- **Actionable insight:** Target this demographic more
- **Strategy shift:** Midwest podcasts vs Super Bowl ads
- **Resource allocation:** Focus where results happen

---

## Stitch Fix Segmentation Example

**The Discovery:**
- 10% of customer base → 60% of sales volume
- 40% of customer base → 10% of sales volume

**Strategic Decisions:**
- **Double Down:** Invest more in high-performing Segment 1
- **Investigate:** Why is Segment 1 outperforming?
- **Fold:** Stop onboarding low-performing segments
- **Reallocate:** Resources to better performing segments

**Same thinking applies to your queries!**

---

## Applying Segmentation to RAG

**Query Performance Patterns:**
- **Amazing Performance** - Queries to highlight and showcase
- **Good Performance** - Queries to double down on and target
- **Poor Performance** - Queries needing targeted improvements
- **Lost Causes** - Queries to abandon (not worth the investment)

**Segmentation Dimensions:**
- Role or organization ID
- Customer cohort or lifecycle stage  
- Psychographics (attitudes, values, interests)
- Query embeddings and summaries
- Chat history patterns

---

## Query Tagging and Classification

**Example Query:** "What's the difference between 2022 vs 2023 budgets?"

**Automatic Tags:**
- `time_filter_required`
- `multiple_queries_needed` 
- `financial_domain`
- `comparative_analysis`

**Analysis Opportunities:**
- Group by time queries → frequency analysis
- Customer satisfaction by query type
- Performance differences across segments
- Resource allocation decisions

---

## The Segmentation Formula

### Expected Value Equation

```
Expected Value = Σ (Impact × Percentage of Queries × Probability of Success)
                 across all segments
```

**Where:**
- **Impact** = Economic value of solving this query type
- **Percentage of Queries** = How often this segment occurs  
- **Probability of Success** = How well your system handles it

**This is how you improve your application systematically!**

---

## Understanding the Levers

### Impact (Economic Value)
- **Revenue generation potential**
- **Cost savings from automation**
- **User satisfaction correlation**
- **Strategic business importance**

*Usually determined by user feedback and research*

### Percentage of Queries (Volume)
- **UX design decisions**  
- **User education and onboarding**
- **Feature discoverability**
- **Customer behavior patterns**

*You have some control here through product decisions*

---

## Understanding the Levers (continued)

### Probability of Success (Performance)
- **Generation quality**
- **Citation accuracy**
- **Text chunk relevance**  
- **User upvote correlation**
- **Task completion rates**

*This is what you optimize through technical improvements*

**Key Insight:** Build specialized systems to maximize each segment's probability of success!

---

## Practical Implementation

### Step 1: Clustering and Classification
- **Clustering models** for initial query grouping
- **Few-shot classifiers** for conversation analysis
- **Batch processing** for historical data
- **Online classification** for real-time segmentation

### Step 2: Monitoring and Analysis
- Track segment performance over time
- Historical trend analysis
- Success rate by segment
- Resource allocation tracking

---

## The Strategic Decision Framework

### For Each Segment, Ask:

**1. Double Down (High Value)**
- High impact × High volume × Improving success rate
- **Action:** Invest more resources, build specialized tools

**2. Investigate (High Potential)** 
- High impact × High volume × Low success rate
- **Action:** Research why it's failing, targeted improvements

**3. Optimize (Steady Performance)**
- Medium impact × Medium volume × Good success rate  
- **Action:** Incremental improvements, maintain quality

**4. Fold (Not Worth It)**
- Low impact × Low volume × Poor success rate
- **Action:** Stop investing, redirect users, abandon segment

---

## Real-World Segmentation Examples

### Query Type Segments
- **Simple Factual** ("What is X?") - High volume, high success
- **Complex Analysis** ("Compare X vs Y over time") - High value, needs work
- **Procedural** ("How do I do X?") - Medium value, good performance  
- **Ambiguous** ("Tell me about stuff") - Low value, poor performance

### Business Context Segments  
- **Sales Team** queries - High business impact
- **Support Team** queries - High volume, cost savings
- **Executive** queries - Low volume, strategic importance
- **General Employee** queries - High volume, mixed value

---

## Success Metrics by Segment

### Technical Metrics
- **Retrieval accuracy** (precision/recall by segment)
- **Response relevance** (human evaluation scores)
- **Citation quality** (verifiable sources percentage)
- **Latency** (response time by complexity)

### Business Metrics
- **Task completion rate** (user achieved their goal)
- **User satisfaction** (thumbs up/down by segment) 
- **Return usage** (came back to ask more questions)
- **Escalation rate** (had to ask human for help)

---

## Implementation Tools and Techniques

### Clustering Approaches
```python
# Semantic clustering of queries
embeddings = embed_queries(query_list)
clusters = KMeans(n_clusters=10).fit(embeddings)

# Topic modeling for themes
topics = LatentDirichletAllocation(n_topics=15).fit(query_texts)
```

### Classification Systems
```python
# Few-shot classification for segments
classifier = FewShotClassifier(
    examples={
        "financial": ["budget", "cost", "revenue queries..."],
        "technical": ["how to", "configure", "troubleshoot..."], 
        "comparative": ["vs", "difference", "compare..."]
    }
)
```

---

## Resource Allocation Strategy

### High-Impact, High-Volume Segments
- **Dedicated engineering team**
- **Specialized embedding models**  
- **Custom retrieval systems**
- **Advanced reranking**

### Medium-Impact Segments
- **Shared engineering resources**
- **Configuration-based improvements**
- **A/B testing optimization**

### Low-Impact Segments  
- **Automated improvements only**
- **User education to redirect**
- **Consider deprecation**

---

## Common Segmentation Mistakes

### ❌ Avoid These Pitfalls

**Over-Segmentation**
- Too many micro-segments
- Analysis paralysis
- Resource fragmentation

**Under-Segmentation**  
- "One size fits all" approach
- Missing optimization opportunities
- Poor resource allocation

**Static Segmentation**
- Set it and forget it
- Missing evolving patterns
- Outdated assumptions

---

## Case Study: Query Performance Matrix

| Segment | Volume | Success Rate | Impact | Action |
|---------|--------|-------------|---------|---------|
| Financial Reports | 25% | 45% | High | 🔧 **Investigate & Fix** |
| Simple Q&A | 40% | 85% | Medium | 📈 **Double Down** |
| Code Debugging | 15% | 60% | High | 🎯 **Targeted Improvement** |
| Random Chat | 20% | 30% | Low | 🗑️ **Fold/Redirect** |

**Insight:** Focus engineering on Financial Reports (high impact, fixable), maintain Simple Q&A (working well), and redirect Random Chat users.

---

## Building Your Segmentation System

### Phase 1: Discovery (Week 1-2)
1. **Collect query logs** for 2-4 weeks minimum
2. **Manual labeling** of 200-500 queries  
3. **Initial clustering** to identify patterns
4. **Stakeholder interviews** for impact assessment

### Phase 2: Classification (Week 3-4)
1. **Build classification system** (few-shot or fine-tuned)
2. **Validate accuracy** on held-out set
3. **Process historical data** for baseline metrics
4. **Create monitoring dashboard**

### Phase 3: Action (Week 5-8)
1. **Prioritize segments** using impact/volume/success matrix
2. **Allocate engineering resources** to high-priority segments  
3. **Implement targeted improvements**
4. **Measure improvement and iterate**

---

## Key Questions for Your Team

### Strategic Questions
1. What are our top 5 query segments by volume?
2. Which segments have highest business impact?
3. Where are our biggest success rate gaps?
4. What segments should we abandon?

### Tactical Questions  
1. How do we automatically classify incoming queries?
2. What specialized tools does each segment need?
3. How do we measure success for each segment?
4. How often should we re-evaluate segments?

---

## Success Indicators

### You're Doing Segmentation Right When:

- **Teams have data-driven debates** about resource allocation
- **"Make AI better"** becomes **"Improve financial query segment"**
- **Engineering roadmap** aligns with segment priorities  
- **Business metrics improve** for targeted segments
- **User satisfaction** increases in focus areas
- **Resource waste decreases** on low-value segments

### Red Flags:
- Still making improvements randomly
- Can't explain why you're working on X vs Y  
- No clear success metrics by segment
- Equal effort on all query types

---

## Next Week Preview

**Session 5: Map - Navigating Multimodal RAG**

**Now that you know WHICH segments to focus on...**
- How do we build specialized systems for high-value segments?
- Multimodal retrieval (documents, images, tables, code)
- Contextual retrieval and summarization techniques
- System improvements targeting specific segments

**Come prepared with your segment analysis!**

---

## Homework: Segment Your Data

### This Week's Assignment

1. **Collect Queries** - Gather 2-4 weeks of user queries
2. **Manual Analysis** - Label 100-200 queries by type/theme  
3. **Initial Clustering** - Use embeddings to find natural groupings
4. **Impact Assessment** - Interview stakeholders about query value
5. **Performance Baseline** - Measure current success rates by segment

### Deliverable
- **Segment prioritization matrix** with volume, impact, and success rates
- **Top 3 segments** for targeted improvement
- **Bottom 2 segments** for potential abandonment

**This analysis will guide the rest of the course!**

---

## Key Takeaway

> **Stop trying to make "the AI" better. Start making specific segments better.**

The magic happens when you:
1. **Identify** what's actually valuable to your users
2. **Focus** engineering effort on high-impact segments  
3. **Abandon** segments that aren't worth the investment
4. **Measure** improvements segment by segment

**Segmentation turns RAG from art into science! 🎯**