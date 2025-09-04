# Chapter 0 Slides

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

**Session 0:** Beyond Implementation to Improvement: A Product Mindset for RAG

Jason Liu

---

## Welcome to the Course

**Instructor:** Jason Liu - AI/ML Consultant & Educator

**Mission:** Dismantle guesswork in AI development and replace it with structured, measurable, and repeatable processes.

**Your Commitment:**
- Stick with the material
- Have conversations with teammates  
- Make time to look at your data
- Instrument your systems
- Ask yourself: "What work am I trying to do?"

---

## Who Am I?

**Background:** Computer Vision, Computational Mathematics, Mathematical Physics (University of Waterloo)

**Facebook:** Content Policy, Moderation, Public Risk & Safety
- Built dashboards and RAG applications to identify harmful content
- Computational social sciences applications

**Stitch Fix:** Computer Vision, Multimodal Retrieval  
- Variational autoencoders and GANs for GenAI
- **$50M revenue impact** from recommendation systems
- $400K annual data curation budget
- Hundreds of millions of recommendations/week

---

## Current Focus

**Why Consulting vs Building?**
- Hand injury in 2021-2022 limited typing
- Highest leverage: advising startups and education
- Helping others build while hands recover

**Client Experience:**
- HubSpot, Zapier, Limitless, and many others
- Personal assistants, construction AI, research tools
- Query understanding, prompt optimization, embedding search
- Fine-tuning, MLOps, and observability

---

## Who Are You?

**Cohort Composition:**
- **30%** Founders and CTOs
- **20%** Senior Engineers  
- **50%** Software Engineers, Data Scientists, PMs, Solution Engineers, Consultants

**Companies Represented:**
- OpenAI, Amazon, Microsoft, Google
- Anthropic, NVIDIA, and many others

**Excited to hear about your challenges and experiences!**

---

## Course Structure: 6-Week Journey

### Week 1: Synthetic Data Generation
- Create precision/recall evaluations
- Start with text chunks → synthetic questions
- Build baseline evaluation suite

### Week 2: Fine-Tuning and Few-Shot Examples
- Convert evals to few-shot examples
- Fine-tune models for better performance
- Evaluate rerankers and methodologies

### Week 3: Deploy and Collect Feedback
- Deploy system to real users
- Collect ratings and feedback
- Improve evals with real user data

---

## Course Structure (continued)

### Week 4: Topic Modeling and Segmentation  
- Use clustering to identify valuable topics
- Decide what to double down on vs abandon
- Focus resources on economically valuable work

### Week 5: Multimodal RAG Improvements
- Incorporate images, tables, code search
- Contextual retrieval and summarization
- Target specific query segments

### Week 6: Function Calling and Query Understanding
- Combine all systems with intelligent routing
- Query → Path selection → Multimodal RAG → Final answer
- Complete end-to-end orchestration

---

## Learning Format

**Asynchronous Lectures (Fridays)**
- Watch videos on your schedule
- Take notes and prepare questions

**Office Hours (Tuesdays & Thursdays)**  
- Multiple time zones supported
- Active learning and discussion
- Question-driven sessions

**Guest Lectures (Wednesdays)**
- Industry experts and practitioners
- Q&A with speakers
- Real-world case studies

**Slack Community**
- Ongoing discussions
- Peer support and collaboration

---

## The Critical Mindset Shift

### ❌ Implementation Mindset
- "We need to implement RAG"
- Obsessing over embedding dimensions  
- Success = works in demo
- Big upfront architecture decisions
- Focus on picking "best" model

### ✅ Product Mindset  
- "We need to help users find answers faster"
- Tracking answer relevance and task completion
- Success = users keep coming back
- Architecture that can evolve
- Focus on learning from user behavior

**Launching your RAG system is just the beginning!**

---

## Why Most RAG Implementations Fail

**The Problem:** Treating RAG as a technical project, not a product

**What Happens:**
1. Focus on technical components (embeddings, vector DB, LLM)
2. Consider it "complete" when deployed
3. Works for demos, struggles with real complexity
4. Users lose trust as limitations surface
5. No clear metrics or improvement process
6. Resort to ad-hoc tweaking based on anecdotes

**The Solution:** Product mindset with continuous improvement

---

## The Key Insight: RAG as Recommendation Engine

**Stop thinking:** Retrieval → Augmentation → Generation

**Start thinking:** Recommendation Engine + Language Model

```
User Query → Query Understanding → Multiple Retrieval Paths
                                    ↓
                        [Document] [Image] [Table] [Code]
                                    ↓
                          Filtering & Ranking
                                    ↓
                            Context Assembly
                                    ↓
                              Generation
                                    ↓
                             User Response
                                    ↓
                             Feedback Loop
```

---

## What This Means

### 1. Generation Quality = Retrieval Quality
- World's best prompt + garbage context = garbage answers
- Focus on getting the right information to the LLM

### 2. Different Questions Need Different Strategies
- Amazon doesn't recommend books like electronics
- Your RAG shouldn't use same approach for every query

### 3. Feedback Drives Improvement  
- User interactions reveal what works
- Continuous learning from real usage patterns

---

## What Does Success Look Like?

### Feeling of Success
- **Less anxiety** when hearing "just make the AI better"
- **Less overwhelmed** when told to "look at your data"  
- **Confidence** in making data-driven decisions

### Tangible Outcomes
- Identify high-impact tasks systematically
- Prioritize and make informed trade-offs
- Choose metrics that correlate with business outcomes
- Drive user satisfaction, retention, and usage

---

## The System Approach

**What is a System?**
- Structured approach to solving problems
- Framework for evaluating technologies  
- Decision-making process for prioritization
- Methodology for diagnosing performance
- Standard metrics and benchmarks

**Why Systems Matter:**
- Frees mental energy for innovation
- Replaces guesswork with testing
- Enables quantitative vs "feels better" assessments
- Secures resources through data-driven arguments

---

## RAG vs Recommendation Systems

**The Reality:** RAG is a 4-step recommendation system

1. **Multiple Retrieval Indices** (multimodal: images, tables, text)
2. **Filtering** (top-k selection)  
3. **Scoring/Ranking** (rerankers, relevance)
4. **Context Assembly** (prepare for generation)

**The Problem:** Engineers focus on generation without knowing if right information is retrieved

**The Solution:** Improve search to improve retrieval to improve generation

---

## Experimentation Over Implementation

**Instead of:** "Make the AI better"

**Ask:**
- Why am I looking at this data?
- What's the goal and hypothesis?
- What signals am I looking for?
- Is the juice worth the squeeze?
- How can I use this to improve?

**Success Formula:** Flywheel in place + Consistent effort = Continuous improvement

Like building muscle: track calories and workouts, don't just weigh yourself daily

---

## Course Commitments

### My Commitment to You
- Be online and answer questions
- Provide extensive office hours support
- Share real-world experience and case studies
- Connect you with industry experts

### Your Commitment
- Engage with the material actively
- Look at your own data and systems
- Participate in discussions and office hours
- Apply learnings to your real projects

**Together, we'll transform your RAG from demo to production-ready product**

---

## Key Takeaway

> **Successful RAG systems aren't projects that ship once—they're products that improve continuously.**

The difference between success and failure isn't the embedding model or vector database you choose.

It's whether you treat RAG as:
- **❌ Static implementation** that slowly decays
- **✅ Living product** that learns from every interaction

**Let's build systems that get better every week! 🚀**

---

## Next Week

**Week 1: Kickstart the Data Flywheel**

- Synthetic data generation strategies
- Building precision/recall evaluations
- Creating your evaluation foundation
- "Fake it till you make it" with synthetic data

**Come prepared to look at your data!**