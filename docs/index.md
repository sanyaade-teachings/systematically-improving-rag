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

!!! success "🎓 Get the Complete Course - 20% Off"
    Transform your RAG system with our comprehensive course on Maven.
    
    **Exclusive discount for book readers: Save 20% with code `EBOOK`**
    
    [Get the RAG Playbook Course →](https://maven.com/applied-llms/rag-playbook?promoCode=EBOOK){ .md-button .md-button--primary }

## Trusted by Leading Organizations

This methodology has been battle-tested by professionals at:

<div class="grid two-columns" markdown="1">

| Company                                         | Company
| ----------------------------------------------- | ------------------------------- |
| [OpenAI](https://openai.com)                    | [Anthropic](https://anthropic.com)
| [Google](https://google.com)                    | [Microsoft](https://microsoft.com)
| [TikTok](https://tiktok.com)                    | [Databricks](https://databricks.com)
| [Amazon](https://amazon.com)                    | [Airbnb](https://airbnb.com)
| [Zapier](https://zapier.com)                    | [HubSpot](https://hubspot.com) 
| [Shopify](https://shopify.com)                  | [PwC](https://pwc.com)
| [Booz Allen Hamilton](https://boozallen.com)    | [Bain & Company](https://bain.com)
| [Northrop Grumman](https://northropgrumman.com) | [Visa](https://visa.com)
| [KPMG](https://kpmg.com)                        | [KPMG](https://kpmg.com)

| Company                                           | Company
| ------------------------------------------------- | ------------------------------- |
| [Decagon](https://decagon.ai/)                    | [Anysphere](https://anysphere.com)
| [GitLab](https://gitlab.com)                      | [Intercom](https://intercom.com)
| [Lincoln Financial](https://lincolnfinancial.com) | [DataStax](https://datastax.com)
| [Timescale](https://timescale.com)                | [PostHog](https://posthog.com)
| [Gumroad](https://gumroad.com)                    | [Miro](https://miro.com)
| [Workday](https://workday.com)                    | [Accenture](https://accenture.com)
| [Mozilla](https://mozilla.org)                    | [Redhat](https://redhat.com)
| [Nvidia](https://nvidia.com)                      | 

</div>


## The Problem: Why Most RAG Systems Fail

!!! quote "Real Patterns from the Field"
    After working with dozens of companies, the failure pattern is predictable:

    **Week 1-2:** "Our RAG demo is amazing!"

    **Week 3-4:** "Why are users getting irrelevant results?"

    **Week 5-6:** "Let's try a different model..."

    **Week 7-8:** "Maybe we need better prompts..."

    **Week 9+:** "Our users have stopped using it."

Sound familiar? You're not alone. The issue isn't your technology—it's your approach.

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

## About the Author

Jason Liu is a machine learning engineer with experience at Facebook and Stitch Fix, and has consulted for companies like HubSpot and Zapier on RAG implementations. His background includes computer vision, recommendation systems, and retrieval applications across various domains.


## Ready to Transform Your RAG System?

!!! success "🎓 Get the Complete Course - 20% Off"
    This book is just the beginning. Get hands-on with our comprehensive course that includes:
    
    - **Live workshops** with real-world case studies
    - **Office hours** for personalized guidance
    - **Private community** of 500+ practitioners
    - **Code templates** and implementation guides
    
    **Save 20% with discount code: `EBOOK`**

[Enroll in the RAG Playbook Course →](https://maven.com/applied-llms/rag-playbook?promoCode=EBOOK){ .md-button .md-button--primary }
