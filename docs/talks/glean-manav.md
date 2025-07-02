---
title: "Enterprise Search and Fine-tuning Embedding Models with Glean"
description: "Guest lecture with Manav from Glean on enterprise search, custom embedding models, and optimizing RAG systems for company-specific data"
tags:
  - enterprise search
  - embedding models
  - fine-tuning
  - RAG optimization
  - Glean
---

# Enterprise Search and Fine-tuning Embedding Models with Glean

Study Notes

I recently hosted Manav from Glean for an insightful guest lecture in my "Systematically Improving RAG Applications" course. This session focused on enterprise search and fine-tuning embedding models - a surprisingly underutilized approach that can dramatically improve RAG system performance. Here's what we learned about Glean's approach to optimizing AI and enterprise search through custom embedding models.

What is Glean and why does their approach to enterprise search matter?
Glean has built a comprehensive Work AI platform that unifies enterprise data across various applications (Google Drive, GitHub, Jira, Confluence) into a single system. Their flagship product, the Glean Assistant, leverages this unified data model to generate relevant answers to user questions and automate workflows.

The foundation of their system is their semantic search capability, which Manav emphasized is absolutely critical for enterprise AI success. As he put it, "Search quality matters - you can't have a good RAG system, you can't have a good overall enterprise AI product unless you have good search." This makes intuitive sense - without retrieving the right context from your enterprise data, even the best LLMs will produce hallucinations and incorrect information.

What makes enterprise data uniquely challenging?
Unlike internet data, which has a significant "head problem" where most searches target popular websites or common information sources, enterprise data is far more heterogeneous and doesn't fit neatly into a single mold. Manav explained:

"Enterprise data is very different than internet data... You have your basic document data sources like Google Drive, Google Docs, Confluence, Notion... But you're also working with a bunch of different types of applications, like Slack, which is a messaging platform. You have meetings, which doesn't really meet the standard concept of what a document is. You have GitHub and GitLab... They all behave in slightly different ways."

This diversity requires a robust, generalized unified data model that can handle the nuances of different data types while maintaining security and privacy. Additionally, company-specific language (project names, initiatives, internal terminology) creates another layer of complexity that generic models struggle with.

Key Takeaway: Enterprise search is fundamentally different from web search because of data heterogeneity and company-specific language. A unified data model that can handle diverse data types while preserving security is essential for effective enterprise AI.

Why fine-tune embedding models for each customer?
One of the most fascinating aspects of Glean's approach is that they build custom embedding models for each customer. While many companies focus on using large, general-purpose embedding models, Glean has found that smaller, fine-tuned models often perform better for specific enterprise contexts.

Manav explained their process:

1. Start with a high-performance base model (typically BERT-based)
2. Perform continued pre-training on company data using masked language modeling
3. Convert the language model into an embedding model through various training techniques
4. Continuously update the model as the company evolves

The results are impressive - after six months, they typically see a 20% improvement in search performance just from learning from user feedback and adapting to company changes.

I found it particularly interesting that they prioritize smaller models when appropriate: "When you're thinking about building really performant enterprise AI... you want to also think about using smaller embedding models when you can, because small embedding models when fine-tuned to the domain and the specific task you have in hand can give you a lot better performance compared to just using large LLMs."

How do they generate high-quality training data?
Creating effective training data for fine-tuning embedding models is challenging, especially with enterprise privacy constraints. Glean uses several creative approaches:

1. Title-body pairs: Mapping document titles to passages from the document body
2. Anchor data: Using documents that reference other documents to create relevance pairs
3. Co-access data: Identifying documents accessed together by users in short time periods
4. Public datasets: Incorporating high-quality public datasets like MS MARCO

They also leverage synthetic data generation using LLMs to create question-answer pairs for documents, which is particularly valuable for smaller corpuses with limited user activity.

What I found most impressive was their attention to application-specific nuances. For example, with Slack data, they don't just treat each message as a document. Instead, they create "conversation documents" from threads or messages within a short timespan, then use the first message as a title and the rest as the body. This understanding of how different applications work leads to much higher quality training data.

Key Takeaway: Generating high-quality training data requires understanding the nuances of different enterprise applications. Creative approaches like title-body pairs, anchor data, co-access signals, and synthetic data generation can provide valuable training signals even with privacy constraints.

How do they learn from user feedback?
Once users start interacting with their products, Glean incorporates those signals to further improve their models:

For their search product, they use query-click pairs as direct signals of relevance.

For RAG-only settings (like their Assistant product), where users don't explicitly click on documents, they face a more challenging problem. They implement various approaches:

- Upvote/downvote systems (though these tend to get sparse usage)
- Tracking when users click on citations to read more about a topic
- Monitoring various interaction patterns to infer relevance

I've encountered similar challenges in my consulting work - getting explicit feedback signals for generative AI products is notoriously difficult. Manav's candid acknowledgment that "this is like a pretty hard open question" resonated with me. Their approach of combining multiple weak signals seems pragmatic.

How do they evaluate embedding model quality?
Evaluating embedding models in enterprise settings is particularly challenging because:

1. You can't access customer data directly due to privacy concerns
2. Each customer has a unique model
3. End-to-end RAG evaluation involves many moving parts

Glean's solution is to build "unit tests" for their models - targeted evaluations for specific behaviors they want their models to exhibit. For example, they test how well models understand paraphrases of the same query.

This approach allows them to:

- Set performance targets for each customer's model
- Identify underperforming models before customers experience issues
- Focus optimization efforts on specific areas

I particularly liked Manav's emphasis on isolating and improving individual components: "If you want to really make good tangible progress day by day, isolating and optimizing individual components is always going to be much more scalable than trying to improve everything all together all at once."

What role does traditional search play alongside embeddings?
Despite all the focus on embedding models, Manav emphasized that traditional search techniques remain crucial:

"You don't want to over-index on semanticness or LLM-based scoring as the only thing that your search system should use... you can get a lot more bang for your buck by not using any semanticness at all to answer most questions."

He estimated that for 60-70% of enterprise search queries, basic lexical search with recency signals works perfectly well. Semantic search becomes more important for complex queries, particularly in agent-based systems.

This aligns with my experience - I often tell clients that getting 80% of the way there with full-text search and then adding semantic search as the cherry on top is a practical approach.

Key Takeaway: Don't abandon traditional search techniques in pursuit of embedding-based approaches. A hybrid system that leverages both lexical and semantic search, along with signals like recency and authority, will deliver the best results for enterprise search.

How do they handle document relevance over time?
One interesting question addressed how Glean handles outdated documents that have been superseded by newer information. Their approach centers around a concept they call "authoritativeness," which incorporates:

1. Recency: Newer documents are generally more relevant
2. Reference patterns: Documents that continue to be linked to or accessed remain authoritative
3. User satisfaction signals: Documents that consistently satisfy user queries maintain relevance

For example, a document containing WiFi password information might be old but still highly relevant if people continue to reference it when answering related questions.

This multi-faceted approach to document authority seems more sophisticated than simply prioritizing recent content, which would miss important evergreen documents.

Final thoughts on building enterprise search systems
Manav concluded with several key insights that resonated with me:

1. A unified data model is critical for handling heterogeneous enterprise data
2. Company-specific language matters tremendously for search quality
3. Fine-tuned smaller models often outperform generic large models for specific tasks
4. Learning from user feedback, though challenging, provides invaluable signals
5. Evaluating models through targeted "unit tests" enables scalable quality assessment
6. Traditional search techniques remain powerful and shouldn't be discarded

As someone who's helped many early-stage companies build RAG systems, I found Glean's approach refreshingly pragmatic. They've clearly learned that the path to high-quality enterprise search isn't just about using the latest, largest models, but about understanding the unique characteristics of enterprise data and building systems that address those specific challenges.

The emphasis on company-specific language models particularly stood out to me - this is an area where I've seen many companies struggle when they try to apply generic embedding models to their unique terminology and document structures. Glean's success with this approach suggests that more companies should consider fine-tuning strategies rather than relying solely on off-the-shelf embedding models.
---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
