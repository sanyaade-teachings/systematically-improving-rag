---
title: The RAG Flywheel
description: Data-Driven Product Development for AI Applications
authors:
  - Jason Liu
date: 2025-04-10
---

# The RAG Flywheel

## A Systematic Approach to Building Self-Improving AI Products

_Practical frameworks for building RAG systems that improve through user feedback and measurement_

Most RAG implementations struggle in production because teams focus on model selection and prompt engineering while overlooking the fundamentals: measurement, feedback, and systematic improvement.

This guide presents frameworks developed through real-world experience with companies like HubSpot, Zapier, and others to help you build RAG systems that become more valuable over time.

# Trusted by Professionals from Leading Organizations:

These are the companies that took our masterclass.

<div class="grid two-columns" markdown="1">

| Company                                         | Industry                    |
| ----------------------------------------------- | --------------------------- |
| [OpenAI](https://openai.com)                    | AI Research & Development   |
| [Anthropic](https://anthropic.com)              | AI Research & Development   |
| [Google](https://google.com)                    | Search Engine, Technology   |
| [Microsoft](https://microsoft.com)              | Software, Cloud Computing   |
| [TikTok](https://tiktok.com)                    | Social Media                |
| [Databricks](https://databricks.com)            | Data Platform               |
| [Amazon](https://amazon.com)                    | E-commerce, Cloud Computing |
| [Airbnb](https://airbnb.com)                    | Travel                      |
| [Zapier](https://zapier.com)                    | Automation                  |
| [HubSpot](https://hubspot.com)                  | Marketing Software          |
| [Shopify](https://shopify.com)                  | E-commerce Platform         |
| [PwC](https://pwc.com)                          | Professional Services       |
| [Booz Allen Hamilton](https://boozallen.com)    | Consulting                  |
| [Bain & Company](https://bain.com)              | Consulting                  |
| [Northrop Grumman](https://northropgrumman.com) | Aerospace & Defense         |
| [Visa](https://visa.com)                        | Financial Services          |
| [KPMG](https://kpmg.com)                        | Professional Services       |

| Company                                           | Industry                        |
| ------------------------------------------------- | ------------------------------- |
| [Decagon](https://decagon.ai/)                    | Technology                      |
| [Anysphere](https://anysphere.com)                | AI                              |
| [GitLab](https://gitlab.com)                      | Software Development            |
| [Intercom](https://intercom.com)                  | Customer Engagement             |
| [Lincoln Financial](https://lincolnfinancial.com) | Financial Services              |
| [DataStax](https://datastax.com)                  | Database Technology             |
| [Timescale](https://timescale.com)                | Database Technology             |
| [PostHog](https://posthog.com)                    | Product Analytics               |
| [Gumroad](https://gumroad.com)                    | E-commerce Platform             |
| [Miro](https://miro.com)                          | Collaboration                   |
| [Workday](https://workday.com)                    | Enterprise Software             |
| [Accenture](https://accenture.com)                | Consulting, Technology Services |
| [Mozilla](https://mozilla.org)                    | Non-profit                      |
| [Redhat](https://redhat.com)                      | Software Development            |
| [Nvidia](https://nvidia.com)                      | AI                              |

</div>

## Who Uses This Approach

This methodology has been used by engineers and data scientists at companies including Zapier, Adobe, Red Hat, and others to build production RAG systems with measurable improvements in user satisfaction and business outcomes.

## The Problem: Why Most RAG Systems Fail

!!! quote "Real Patterns from the Field"
After working with dozens of companies, the failure pattern is predictable:

    **Week 1-2:** "Our RAG demo is amazing!"
    **Week 3-4:** "Why are users getting irrelevant results?"
    **Week 5-6:** "Let's try a different model..."
    **Week 7-8:** "Maybe we need better prompts..."
    **Week 9+:** "Our users have stopped using it."

Sound familiar? You're not alone. The issue isn't your technology—it's your approach.

!!! info "Get Updates"
Subscribe for updates on new content and frameworks:

    [Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

## The Solution: The RAG Improvement Flywheel

### [Introduction: The Product Mindset Shift](workshops/chapter0.md)

**The Foundation That Changes Everything**

Stop thinking like an engineer. Start thinking like a product leader. Learn why treating RAG as a product rather than a project is the #1 predictor of success.

**Key concepts:** The improvement flywheel • Common failure patterns • Product thinking vs implementation thinking

---

### [Chapter 1: Starting the Data Flywheel](workshops/chapter1.md)

**From Zero to Evaluation in Days, Not Months**

The cold-start problem kills most RAG projects. Learn the synthetic data techniques that get you from zero to measurable improvement in days.

**You'll build:** Synthetic evaluation datasets • Precision/recall frameworks • Leading vs lagging metrics • Experiment velocity tracking

**Case study:** Legal tech company improved retrieval from 63% to 87% in 2 weeks using these techniques

---

### [Chapter 2: From Evaluation to Enhancement](workshops/chapter2.md)

**Fine-Tuning That Actually Moves Business Metrics**

Stop guessing which model to use. Learn how to systematically improve retrieval through fine-tuning, re-ranking, and targeted enhancements.

**You'll implement:** Embedding fine-tuning pipelines • Re-ranker integration (12-20% improvement) • Hard negative mining • A/B testing frameworks

**Case study:** E-commerce company increased revenue by $50M through systematic improvements

---

### [Chapter 3: User Experience and Feedback](workshops/chapter3-1.md)

**5x Your Feedback Collection with One Simple Change**

The secret to improvement? Getting users to tell you what's wrong. Learn the UX patterns that transform silent users into active contributors.

**You'll master:** High-converting feedback copy • Citation UX for trust • Implicit signal collection • Enterprise Slack integrations

**Case study:** Changing "How did we do?" to "Did we answer your question?" increased feedback 5x

---

### [Chapter 4: Understanding Your Users](workshops/chapter4-1.md)

**Segmentation Strategies That Reveal Hidden Opportunities**

Not all queries are equal. Learn to identify high-value user segments and build targeted solutions that delight specific audiences.

**You'll discover:** Query pattern analysis • User segmentation techniques • Priority matrices • Resource allocation frameworks

**Case study:** SaaS company found 20% of queries drove 80% of value, focused efforts accordingly

---

### [Chapter 5: Building Specialized Capabilities](workshops/chapter5-1.md)

**Build Purpose-Built Retrievers That Users Love**

One-size-fits-all RAG is dead. Learn to build specialized retrievers for documents, code, images, and structured data.

**You'll create:** Document-specific retrievers • Multi-modal search • Table/chart handlers • Domain-specific solutions

**Case study:** Construction blueprint search improved from 27% to 85% recall with specialized approach

---

### [Chapter 6: Unified Product Architecture](workshops/chapter6-1.md)

**Unified Systems That Route Intelligently**

Tie it all together with routing architectures that seamlessly direct queries to specialized components while maintaining a simple user experience.

**You'll architect:** Query routing systems • Tool selection frameworks • Performance monitoring • Continuous improvement pipelines

**Case study:** Enterprise system handling millions of queries with 95%+ routing accuracy

---

### [Conclusion: Product Principles for AI Applications](misc/what-i-want-you-to-takeaway.md)

**The Lessons That Survive Every Technology Shift**

Models change. Principles endure. Take away the core insights that will guide your AI product development for years to come.

## Learn from Industry Leaders: 20+ Expert Talks

!!! info "Featured Lightning Lessons"
Companies like Zapier, ChromaDB, LanceDB, Glean, and Sourcegraph share their battle-tested strategies

### Featured Talks

**[How Zapier 4x'd Their AI Feedback](talks/zapier-vitor-evals.md)** - Vitor (Staff Engineer, Zapier) reveals the one-line change that transformed their feedback collection

_"Jason helped us set you on the right path... emphasis on looking at your data and building a metrics-based flywheel."_ - **Vitor**, Staff Software Engineer, Zapier

**[The 12% RAG Boost You're Missing](talks/fine-tuning-rerankers-embeddings-ayush-lancedb.md)** - Ayush (LanceDB) shows why re-rankers are the "low-hanging fruit" everyone ignores

**[Why Cline Ditched RAG Entirely](talks/rag-is-dead-cline-nik.md)** - Nik Pash explains why leading coding agents abandoned embeddings for direct exploration

**[The RAG Mistakes Killing Your AI](talks/rag-antipatterns-skylar-payne.md)** - Skylar Payne exposes the anti-patterns that 90% of teams fall into

**[Stop Trusting MTEB Rankings](talks/embedding-performance-generative-evals-kelly-hong.md)** - Kelly Hong reveals why public benchmarks fail in production

[Explore all 20+ talks →](talks/index.md)

## For Product Leaders, Engineers, and Data Scientists

!!! info "What You'll Learn"
**For Product Leaders**

    - How to establish metrics that align with business outcomes
    - Frameworks for prioritizing AI product improvements
    - Approaches to building product roadmaps for RAG applications
    - Methods for communicating AI improvements to stakeholders

    **For Engineers**

    - Implementation patterns that facilitate rapid iteration
    - Architectural decisions that enable continuous improvement
    - Techniques for building modular, specialized capabilities
    - Approaches to technical debt management in AI systems

    **For Data Scientists**

    - Methods for creating synthetic evaluation datasets
    - Techniques for segmenting and analyzing user queries
    - Frameworks for measuring retrieval effectiveness
    - Approaches to continuous learning from user interactions

## Quick Improvements

Common improvements that can be implemented quickly:

**1. Improve Feedback Collection**

- Replace "How did we do?" with "Did we answer your question?"
- More specific questions get better response rates

**2. Better Data Formatting**

- Format structured data as markdown tables instead of JSON/CSV
- Use XML for complex tables
- Improves lookup accuracy for structured information

**3. Show Progress to Users**

- Display "Searching... Analyzing... Generating..." with progress indicators
- Stream responses as they're generated
- Reduces perceived latency

**4. Page-Level Chunking**

- For documentation, chunk by page boundaries rather than arbitrary text length
- Pages often contain semantically coherent units

**Medium-Term Improvements (2-4 weeks)**

- **Fine-tune embeddings**: Cost-effective way to improve domain-specific performance
- **Add re-ranker**: Secondary ranking step that improves retrieval relevance
- **Build specialized tools**: Domain-specific retrievers for documents, code, or structured data
- **Implement contextual retrieval**: Better understanding of query context
- **Create Slack feedback integration**: Collect feedback directly in enterprise workflows

!!! info "Learn from the Experts"

    Before implementing, learn from these practical talks:
    - [**RAG Anti-patterns in the Wild**](talks/rag-antipatterns-skylar-payne.md)
    - [**Document Ingestion Best Practices**](talks/reducto-docs-adit.md)

## About the Author

Jason Liu is a machine learning engineer with experience at Facebook and Stitch Fix, and has consulted for companies like HubSpot and Zapier on RAG implementations. His background includes computer vision, recommendation systems, and retrieval applications across various domains.

## Getting Started

Begin your journey by reading the [Introduction](workshops/chapter0.md) or jump directly to [Chapter 1](workshops/chapter1.md) to start building your evaluation framework and data foundation.

---

--8<--
"snippets/enrollment-button.md"
--8<--

---
