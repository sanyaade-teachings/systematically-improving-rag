# Chapter2 Slides

*Extracted from PDF slides using docling*

---

jxnl.co

@jxnlco

## Systematically Improving RAG Applications

Session 2

If you're not fine -tuning, you're Blockbuster, not Netflix Jason Liu

## Overview of RAG Playbook

## Sessions 1-3: Part 1

Session 4-6: Part 2

Building synthetic data, fine-tuning, and collecting user data and product

Split, Map, Apply: Build search indices and query routing systems separately

Generate synthetic data

Generate fast evaluations

Use evals dataset to start finetuning

Build a UX that feels fast and collects data for.. More evals!

Refine and improve query routing system

Segment Input queries to identity new topics and capabilities to invest in

Explore new search indices or new metadata to better answer questions for a specific query segments (i.e., by generating synthetic questions)

<!-- image -->

<!-- image -->

## The challenge with using providers' existing embeddings

How to improve representations

How to improve representations

Homework for this session

Homework for this session

Next session

Next session

Embedding models translate human-readable text into machine-readable and searchable vectors .

<!-- image -->

## Why does implementing a provider's existing embedding model fail?

<!-- image -->

## Why does implementing a provider's existing embedding model fail?

<!-- image -->

We assume that the embedding model understands the user's intent and context

For example, after a user adds a red shirt to cart, we don't know if the user wants

- · More similar red shirts
- · More shirts of different colors in a similar fashion (e.g., V-neck)
- · Pants, shoes, or a bag that may complement the red shirt as a part of an outfit

The model will only return high cosine similarity shirts maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Why does implementing a provider's existing embedding model fail? The Distance Assumption

- · distance(embed(query), embed(chunk))
- · distance(embed(song), embed(user))
- o ~ P(relevant)
- · distance(embed(user), embed(product))
- o ~ P(purchase)
- · distance(embed(product), embed(product))
- o ~ P(substitutable)
- o ~ P(complementary)
- o ~ P(same cart) ~ ???
- o ~ P(listen)
- o ~ P(add to playlist)
- o ~ ???
- · distance(embed(song) ,embed(song))
- o ~ P(same playlist)
- o ~ P(liked by same people)
- o ~ P(same style)
- o ~ ???

<!-- image -->

Using a providers embedding model bakes many assumptions on what similarity means

All that exists is the dataset we trained on

## Dating app example

## Are these similar or different?

<!-- image -->

'I love coffee'

<!-- image -->

'I hate coffee'

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Dating app example

## Are these different or similar?

<!-- image -->

## Answer: It depends

## Different

- · In the context of a dating profile , users who love coffee likely don't want to date users who hate coffee

## Similar

- · In the context of a dating profile, both users may be foodies. This might demonstrate strong preferences for food and drink (e.g., one loves tea, one hates coffee)

## Dating app example

## Are these different or similar?

<!-- image -->

'I love coffee'

<!-- image -->

'I hate coffee'

## Answer: It depends

## Key takeaway:

- · Ultimately, these questions don't matter in isolation. Even if OpenAI's embedding model has data on comparing texts, the objective function is very different based on your product
- · For dating apps, we want to build a model that takes two profiles, compares them, predicts whether they will like each other (swipe left, send a super like), go on a date

<!-- image -->

## What does this mean for you?

There is likely a significant gap between the text embeddings and the rankers you currently use, versus what would constitute a successful match.

<!-- image -->

## What does this mean for you?

It's important to set up your logging now to collect the data needed to train and fine-tune an embedding model or reranker model.

<!-- image -->

<!-- image -->

The challenge with using providers' existing embeddings

The challenge with using providers' existing embeddings

How to improve representations

How to improve representations

## Include more data or generate synthetic data

Finetuning and re-rankers

Finetuning and re-rankers

Homework for this session

Homework for this session

Next session

Next session

## Better Representations = More Data

## Key takeaway:

- · Don't assume the question embedding and the object embedding (e.g., the answer text embedding) will be similar for some definition
- · The objective of similarity is weak and there's likely going to be something better

## Example

- · Dating apps: For two bios, do they like each other?
- · Music recommendation : Given two songs, what's the likelihood they're on the same playlist?

<!-- image -->

## What if I have no data?

- … Synthetic data again

## Leveraging Synthetic data

All the experience of generating synthetic data to test our precision and recall can now be reapplied to train a model that optimizes recall!

- · For all the tasks where we evaluated the success of the search system using recall and embeddings we can now consider building finetuning data that is trained to improve recall
- · Examples of datasets now look like:
- o Queries -&gt; Image summaries
- o Queries -&gt; Code Snippet
- o Queries -&gt; Table Summaries
- o Queries -&gt; Chunks
- o Queries -&gt; Table Chunks
- o Queries -&gt; Tool Descriptions

## We can:

- · We can also use this dataset to finetune
- · We can also use LLMs to add better relevancy
- · Allow us to improve everything we do over these 6 weeks

## Leveraging Synthetic data

All the experience of generating synthetic data to test our precision and recall can now be reapplied to train a model that optimizes recall!

- · For all the tasks where we evaluated the success of the search system using recall and embeddings we can now consider building finetuning data that is trained to improve recall
- · Examples of datasets now look like:
- o Queries -&gt; Image summaries
- o Queries -&gt; Code Snippet
- o Queries -&gt; Table Summaries
- o Queries -&gt; Chunks
- o Queries -&gt; Table Chunks
- o Queries -&gt; Tool Descriptions

## How this helps monitoring:

This embedding model, now equipped with the knowledge of your data, will likely perform better for:

- · Embedding-based topic modeling
- · Embedding-based classification

## We can:

- · We can also use this dataset to finetune
- · We can also use LLMs to add better relevancy
- · Allow us to improve everything we do over these 6 weeks

<!-- image -->

Everything we're using large language models (LLMs) for is what I had to pay data labeling teams hundreds of thousands of dollars for every year.

This is the ML playbook, but previously only possible at large companies

<!-- image -->

<!-- image -->

Historically, we build a product to collect data Then use it to train a model Then release a new product

<!-- image -->

- LLMs just allow us to do this backwards

This is our wax on, wax off, Mr. Miyagi moment.

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

The challenge with using providers' existing embeddings

The challenge with using providers' existing embeddings

How to improve representations

How to improve representations

Include more data or generate synthetic data

Include more data or generate synthetic data

## Finetuning and re-rankers

Homework for this session

Next session

Homework for this session

Next session

## So what happens when we finetune?

Create triplet examples (anchor and positive have same label, negative has different label)

## Before fine-tuning

## After fine-tuning

<!-- image -->

## So what happens when we finetune?

Create triplet examples (anchor and positive have same label, negative has different label)

## Before fine-tuning

## After fine-tuning

<!-- image -->

## Case study: Improving Retrieval on Ramp with Transaction Embeddings

## Additional reading:

https://engineering.ramp.com/transaction-embeddings

## Before fine-tune

## After fine-tune

<!-- image -->

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Case study: Improving Retrieval on Ramp with Transaction Embeddings

Additional reading: https://engineering.ramp.com/transaction-embeddings

<!-- image -->

<!-- image -->

## What does the data look like?

- 1. With enough examples, your model will ultimately learn your objective
- 2. Examples:
- · query, passage, is\_relevant (could be bootstrapped by LLM)
- · query, passage, is\_cited (to provide even higher signal)
- 3. Consider both pair and triplet examples
- 4. If you have high quality data, you can still use the dataset to train both biencoders and cross-encoders, and even ColBERT models
- · You'll still need both!

```
question: str question:str positive_examples: List[str] answer: str negative_examples: List[str]
```

@jxnlco @jxnlco maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## What does the data look like?

- 1. With enough examples, your model will ultimately learn your objective
- 2. Examples:
- · query, passage, is\_relevant (could be bootstrapped by LLM)
- · query, passage, is\_cited (to provide even higher signal)
- 3. Consider both pair and triplet examples
- 4. If you have high quality data, you can still use the dataset to train both biencoders and cross-encoders, and even ColBERT models
- · You'll still need both!

question:

str

question:str

positive\_examples: List[str]

answer:

str

negative\_examples: List[str]

@jxnlco @jxnlco

## Remember: your data is your moat, not the model!

- 1. Think about your models not as models but as data and unique application objectives
- 2. Especially with Cohere's re-ranking API, you can fine-tune and serve embedding models at scale optimized for your use case
- 3. You may also wonder how much data you need to fine-tune embeddings
- · My experiment: with 1000 examples, you can start to outperform OpenAI (with the correct feedback)!

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## "anchor": "What are the main causes of climate change?"

## pos" : [

land use such as deforestation, and industrial processes. These human activities increase the concentration of heat-trapping gases in the Earth 5 atmosphere.

"Climate change is primarily caused by human activities that release greenhouse gases into the atmosphere. The burning of fossil fuels for energy, deforestation, and industrial processes are major contributors\_ "The main drivers of climate change include the emission of greenhouse gases from burning fossil fuels . changes in

1 ,

## neg" : [

"The Earth' s climate has changed throughout history. Just in the last 650,000 years there have been seven of glacial advance and retreat, with the abrupt end of the last ice age about 11,700 years ago marking the beginning of the modern climate era and of human civilization. cycles

"Climate change mitigation involves reducing greenhouse gas emissions and enhancing sinks that absorb greenhouse gases from the atmosphere.

<!-- image -->

## Coffee example

## Are these similar or different?

<!-- image -->

## Process

## Push things that go together closer and push things that don't go together further apart

- 1. Initialize the 3 example vectors (anchor, positive, negative) with random numbers
- 2. The ML system will bring complementary things closer and distant things further
- 3. Depending on how we curate this data, we can start enforcing opinions of our model
- · Option 1: 'I love coffee' &amp; 'I love tea' are similar to each other and dissimilar to 'I hate tea'
- · Option 2: 'I love tea' &amp; 'I hate tea' are the same because of positive vs. negative preferences, while 'I like coffee' is different

## Additional datasets:

https://sbert.net/docs/sentence\_transformer/dataset\_overview.html maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

<!-- image -->

<!-- image -->

## Quickstart

<!-- image -->

- Quickstart

## Quickstart

## Sentence Transformer

Characteristics of Sentence Transformer (a.k.a bi-encoder) models:

- 1. Calculates a fixed-size vector representation (embedding) given texts or images.
- 2. Embedding calculation is often efficient; embedding similarity calculation is very fast.
- 3.
- 4. Often used as a first step in a two-step retrieval process; where a Cross-Encoder (a.ka. reranker) model is used to re-rank the top-k results from the bi encoder.

Once you have installed Sentence Transformers; you can easily use Sentence Transformer models:

from sentence\_transformers import SentenceTransformer

Load pretrained Sentence Transformer model model SentenceTransformer("all-MiniLM-L6-v2" )

- The sentences to encode

sentences

'The weather is lovely today.

"It's so sunny outside

"He drove to the stadium

2 . Calculate embeddings by cal model .encode( ) embeddings model.encode(sentences ) print (embeddings.shape) [3 , 384 ] ling

- 3 . Calculate the embedding similarities

similarities model.similarity(embeddings, embeddings) print(similarities)

tensor( [ [1.0000, 0.6660 , 0.1046] ,

[0.6660 , 1.0000 0.1411]

- [0.1046,

0.1411 1.0000]])

## Documentation

- 1 SentenceTransformer
- 2 SentenceTransformer.encode
- 3. SentenceTransformer.similarity

## Other useful methods and links:

- SentenceTransformer.similarity rwise pai
- SentenceTransformer Usage
- SentenceTransformer Pretrained Models
- SentenceTransformer Training Overview
- SentenceTransformer &gt; Dataset Overview
- SentenceTransformer Loss Overview
- SentenceTransformer Training Examples

## Edit on GitHub

<!-- image -->

## https://huggingface.co/blog/modernbert

maven.com/applied-llms/rag-playbook

<!-- image -->

<!-- image -->

## https://docs.cohere.com/docs/rerank-preparing-the-data

<!-- image -->

<!-- image -->

## How much data do we need?

<!-- image -->

## Do we need to train task-specific models?

- 1. If you have multiple representations:
- · Questions and summaries
- · Questions and chunks
- · Questions and table/image summaries
- 2. These can all be mixed into a blend of training data to train a single model (eventually this can be used to replace OpenAI embeddings and the re-rankers
- 3. In many cases multiple 'tasks' trained jointly can yield better results
- 4. It's unlikely that training the cosine distance or improving the cosine model will eliminate the need for the re -ranker
- · This can improve latency and precision recall trade-offs by having a two-tiered approach
- 5. Start collecting this data now because you'll need it some point in the future (as you expand your teams, you want to have the data ready for them to work with)

## Fine-Tuning Encoders &amp; Cross-Encoders in RAG: Case Studies and Implementations

| Case Study / Implementation                                                                                 | Description                                                                                | Performance Gains                                                     | Source   |
|-------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|----------|
| Enhancing Q&A Text Retrieval with Ranking Models: Benchmarking, fine-tuning and deploying Rerankers for RAG | Fine-tuned cross-encoder applied for reranking in a QA pipeline                            | 14% accuracy boost over baseline retrieval                            | Link     |
| Improving the Domain Adaptation of (RAG) Models for Open Domain Question Answering                          | Fine-tuning both question and passage encoders in a RAG system for domain adaptation.      | ~12% increase in Exact Match accuracy                                 | Link     |
| Re-ranking in Retrieval Augmented Generation: How to Use Re-rankers in RAG                                  | Adding a fine-tuned cross-encoder on top of a dense retriever for customer support systems | 20% boost in response accuracy; 30% reduction in irrelevant documents | Link     |

<!-- image -->

If you want to host your embedding models, a great place to check out is Modal Labs.

Check out my post on embedding all of Wikipedia in 15 minutes.

https://modal.com/blog/embedding-wikipedia

If you want to fine the best finetuned model Check out my post on grid searching models using 50 GPUS

https://modal.com/blog/fine-tuning-embeddings

<!-- image -->

<!-- image -->

The challenge with using providers' existing embeddings

The challenge with using providers' existing embeddings

How to improve representations

How to improve representations

## Homework for this session

Next session

Next session

## Homework

<!-- image -->

## Finish homework from last session

- · Generate synthetic data to test your system (evaluation data set)
- · Establish a baseline to run experiments on
- o Check BM25, Embeddings, Chunkers, and Rerankers (LanceDB)
- o With baselines, we can 'do nothing' if experiments don't pan out
- · Review user queries: Sample some % of user traffic and run the LLM Ranker over retrieved text chunks and monitor questions that have low precision
- · Start to build process and flywheel: Establish regular cadence to review questions or documents that get poor recall or even just low cosine or reranker scores

<!-- image -->

<!-- image -->

Homework for this session: Focus on improving representations

- · For each set of subtasks we will have baseline recall metrics
- o Query -&gt; Chunk
- o Query -&gt; Snippets
- o Query -&gt; X
- · Which ones need improvement the most?
- · Can we prepare a triplets dataset?
- o Does Cohere Rerankers Finetuning improve recall for my task?
- o Do I have enough data (500-1000) to finetune and embedding model?
- · Does it make sense to self host an embedding model?

<!-- image -->

<!-- image -->

The challenge with using providers' existing embeddings

The challenge with using providers' existing embeddings

How to improve representations How to improve representations

Homework for this session

Homework for this session

## Next session

## Overview of next week

## · Focus for last sessions:

- · Understand the RAG playbook and how to implement it
- · Review how to use the RAG playbook steps (e.g., generate synthetic data, focus on recall-precision metrics) to tackle the query routing sub-problem while improving RAG applications
- · Focus of this sessions:
- · Understand the major challenges with representations
- · Implement solutions to improve representations
- · Focus for next sessions:
- · Session 3: The Art of RAG UX - Turning Design into Data

<!-- image -->