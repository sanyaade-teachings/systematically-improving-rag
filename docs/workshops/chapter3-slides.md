# Chapter3 Slides

*Extracted from PDF slides using docling*

---

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

Session 3

The Art of RAG UX: Turning Design into Data

Jason Liu

<!-- image -->

## Overview

## Three goals for today

- 1. Makes sure we're taking actions to collect feedback
- 2. Expand on what is possible with streaming
- 3. Give you a small set of prompting and UX tips to improve satisfaction and quality

Consider this mostly a survey of other techniques that I apply. This does not fit neatly into the other sections this course.

The past two sessions have been around: faking data, creating synthetic data, in hopes that one day user data will supplement the work that we're doing. ''

This session, the goal is to figure out how we can collect that user data and how can we give the users a good experience?

<!-- image -->

<!-- image -->

## Collecting more feedback

Streaming for better user satisfaction

Streaming for better user satisfaction

Prompting and Chain of Thought

Prompting and Chain of Thought

## Look at your data

<!-- image -->

<!-- image -->

Getting user feedback is the second most important thing you can be doing after looking at your input data

<!-- image -->

https://claude.site/artifacts/d57936fe-03c1-4815-8511cbdb507d6d9c

<!-- image -->

## Don't be subtle

https://claude.site/artifacts/d57936fe-03c1-4815-8511cbdb507d6d9c

<!-- image -->

@jxnlco @jxnlco

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

<!-- image -->

## Don't be subtle

https://claude.site/artifacts/d57936fe-03c1-4815-8511cbdb507d6d9c

<!-- image -->

@jxnlco @jxnlco

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

<!-- image -->

## Don't be subtle

https://claude.site/artifacts/d57936fe-03c1-4815-8511-cbdb507d6d9c

<!-- image -->

<!-- image -->

All this feedback can be used as part of your segmentation and exploration.

## Question:

- · Are there certain question segments that fall victim to these failure modes?
- · Could we predict if a question might lead to a failure mode?

## Feedback from enterprise customers

All of this works well for consumer cases. For enterprise, we'll have to try a lot harder

<!-- image -->

<!-- image -->

We need to hear about your negative feedback. It's essential in order for us to improve our application

What you share with us will be discussed:

- · In a shared channel with Customer Success
- · At our weekly/bi-weekly syncs

We'll bring up this negative feedback, add it to our evaluation framework (set), and report back to you how much they have improved over time

This is how we can drive the volume of feedback for our customers while building trust, collecting data, and building evals

<!-- image -->

we can also use feedback it to improve our re-rankers and our embedding models (session 2).

For example, re-labeling data if the feedback is about relevance

<!-- image -->

## Recall from our fine tune section the notion of triplets

## So what happens when we finetune?

Create triplet examples (anchor and positive have same label, negative has different label)

## Before fine-tuning

## After fine-tuning

<!-- image -->

<!-- image -->

The hardest part of this task is actually about finding the negative examples.

## Finding Hard Negatives

Consider Facebook's people you may know  feature

<!-- image -->

@jxnlco @jxnlco https://claude.site/artifacts/8bf394073a66-46be-84ff-a042a4161485

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Finding Hard Negatives

Consider Facebook's people you may know  feature

<!-- image -->

@jxnlco @jxnlco https://claude.site/artifacts/8bf394073a66-46be-84ff-a042a4161485

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

<!-- image -->

There will be numerous ways to collect positive and negative examples.

I firmly believe that the success of Tinder and Hinge is rooted in the volume of data they collect and their ability to obtain negatives.

- - Lightweight Interaction (Swipe)
- - Positive and Negative interactions (Like, Dislike)
- - Simple objective (Match)

I believe I can do the same thing with citations, allowing us to collect data, while also building more trust in our system

## Building Citations To Improve Trust

https://claude.site/artifacts/14cbd428-0382-44b8-9353-1c06d830b8dc

<!-- image -->

<!-- image -->

## Building Citations :

- · Allow Preview of Citation text
- · Allow Delete/Regenerate in order to give negative feedback

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Building Citations To Improve Trust

<!-- image -->

<!-- image -->

Provide a prompt

## Generate citations to build satisfaction and trust (cont'd)

## &lt;task&gt;

Your task is to provide a summary of the user schedule and important messages , with citations to the original sources . Use the following format for citations: (cited text) [citation number].

&lt;ltask&gt;

&lt;given\_information&gt;

- [2] The user received an email from jasonacompany.com with the subject "Quarterly Report Due" &lt;litem&gt;
- [1] The user has a calendar event: "Marketing Team Meeting" at 2 PM today.&lt;/item&gt;

Generate a brief summary that mentions both the meeting and the email, us citations ing

<!-- image -->

Your response should be in JSON format with a "body" field for the main text and a "citations" array for the citation details.&lt;/stepz

<!-- image -->

## Negative examples: generate citations to build satisfaction and trust (cont'd)

## &lt;task&gt;

Your task is to provide a summary of the user schedule and important messages , with citations to the original sources . Use the following format for citations: (cited text) [citation number]. &lt;ltask&gt;

&lt;given\_information&gt;

- [2] The user received an email from jasonacompany.com with the subject "Quarterly Report Due" .&lt;/item&gt;
- [1] The user has a calendar event: "Marketing Team Meeting" at 2 PM today.&lt;/item&gt;

&lt;Igiven\_information&gt;

Generate a brief summary that mentions both the meeting and the email, us citations ing

Your response should be in JSON format with a "body" field for the main text and a "citations" array for the citation details. &lt;Istepz

<!-- image -->

<!-- image -->

Use consistent formatting for links and employ IDs as pointers maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

| Price (9 May 14, USS):    | 129.45       |
|---------------------------|--------------|
| Target Price (USS):       | 170.00       |
| 52-Week Price Range:      | 55.28-174.98 |
| Market Cap. (USS m):      | 8,196.0      |
| Enterprise Value (USS m): | 9,089.5      |

<!-- image -->

<!-- image -->

<!-- image -->

Collecting more feedback

Collecting more feedback

## Streaming for better user satisfaction

Prompting and Chain of Thought

Prompting and Chain of Thought

## Streaming Overview

- 1. Stream interstitials to explain latency
- 2. Stream results and  UI
- 3. Stream tool calls!

<!-- image -->

<!-- image -->

@jxnlco @jxnlco

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Streaming overview

## Why we should stream:

## Lower perceived wait time

- · Users perceive animated progress bars as 11% faster, even with equal wait times (Harrison et al.).

## Reduce user churn / disengagement

- · Users will tolerate up to 8 seconds of waiting if given visual feedback reducing abandonment (Nah).

## Increase satisfaction and trust

- · Applications with engaging loading screens often report higher user satisfaction scores.
- · Facebook discovered that skeleton screens reduced perceived load times, resulting in better user retention and engagement.

Harrison, C., Yeo, Z., &amp; Hudson, S. E. (2010). Faster progress bars: manipulating perceived duration with visual augmentations. Proceedings of the SIGCHI Conference on Human Factors in Computing Systems.

Nah, F. F. (2004). A study on tolerable waiting time: how long are Web users willing to wait?. Behaviour &amp; Information Technology.

<!-- image -->

## Streaming overview

## Why we should stream:

## Lower perceived wait time

- · Users perceive animated progress bars as 11% faster, even with equal wait times (Harrison et al.).

## Reduce user churn / disengagement

- · Users will tolerate up to 8 seconds of waiting if given visual feedback reducing abandonment (Nah).

## Increase satisfaction and trust

- · Applications with engaging loading screens often report higher user satisfaction scores.
- · Facebook discovered that skeleton screens reduced perceived load times, resulting in better user retention and engagement.

Harrison, C., Yeo, Z., &amp; Hudson, S. E. (2010). Faster progress bars: manipulating perceived duration with visual augmentations. Proceedings of the SIGCHI Conference on Human Factors in Computing Systems.

Nah, F. F. (2004). A study on tolerable waiting time: how long are Web users willing to wait?. Behaviour &amp; Information Technology.

<!-- image -->

## What we can stream:

- · Responses (incl. citations or follow-up questions)
- · Arguments of function calls
- · Interstitials

## We should assess:

- · Track user feedback to understand user demand
- · Migrating to streaming is complex and challenging
- · Understand how much latency matters in your application

If you're thinking about it...

Migrating from non-streaming to streaming is a pain the ass, you either have to build it from the start or it'll take weeks out of your dev cycle to 'upgrade'

It's worth it.

<!-- image -->

Stream and parse the response and other attributes (follow-up actions) in real time

<!-- image -->

https://claude.site/artifacts/8644e9fc-939a-4520-8fa2-58f589f929d3

@jxnlco @jxnlco maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Stream and parse the response and other attributes (follow-up actions) in real time

<!-- image -->

https://claude.site/artifacts/8644e9fc-939a-4520-8fa2-58f589f929d3

@jxnlco @jxnlco

<!-- image -->

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

If you build a lot of follow-up action UI, you can build datasets and again use retrieval to few-shot your prompts to take follow-up actions

<!-- image -->

## Interstitials for explainability

<!-- image -->

@jxnlco @jxnlco https://claude.site/artifacts/bba5efe9-1d4149ff-a43f-05d3d349e193

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Interstitials for explainability

<!-- image -->

@jxnlco @jxnlco https://claude.site/artifacts/bba5efe9-1d4149ff-a43f-05d3d349e193

## Use webhooks, server-sent events, or a generator to stream

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Stream tool arguments and render in UI

<!-- image -->

<!-- image -->

https://claude.site/artifacts/1a2a1e9a-e5d7-4511-a299211d70fdeb3b maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Stream tool arguments and render in UI

<!-- image -->

## Benefits

- · Create UI that allows users to edit and rerun tools
- o This becomes data collection that we can leverage to create better few-shot examples or fine-tuning data.
- · Enables collection of better feedback data
- · Supports analytics on what questions have additional attributes

https://claude.site/artifacts/1a2a1e9a-e5d7-4511-a299211d70fdeb3b maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Simple Example: Slack Bots

As an interstitial, the slack integration can react with the eyes emoji to communicate it has seen the user's message

<!-- image -->

<!-- image -->

## Simple Example: Slack Bots

As an interstitial, the slack integration can react with the eyes emoji to communicate it has seen the user's message

<!-- image -->

Use a checkmark to communicate the bot has finished answering

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Simple Example: Slack Bots

As an interstitial, the slack integration can react with the eyes emoji to communicate it has seen the user's message

<!-- image -->

Use a checkmark to communicate the bot has finished answering

<!-- image -->

Pre-fill emoji reactions (thumbs-up, thumbs-down, star) to communicate to the user there are alternative ways to provide feedback

<!-- image -->

This would be saved as an approved questionanswer pair which could be used in few-shot examples maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

If you see great examples of using interstitials and streaming I would love to see them on Slack in #random

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Collecting more feedback

Collecting more feedback

Streaming for better user satisfaction

Streaming for better user satisfaction

## Prompting and Chain of Thought

## Prompting: Showcase capabilities

Perplexity is always showing off capaibilites trying to guide the user to behavior we perform well in

<!-- image -->

Example queries

Literally a list of capabilities, which likely have different prompts

<!-- image -->

<!-- image -->

In session 4 we'll talk about how to discover them through data analysis maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Provide example and related queries

Focus on capabilities available and dynamically change prompting based on specific use case

<!-- image -->

Special UI elements for sources by type (e.g., video), related queries, etc.

## Provide example and related queries

Focus on capabilities available and dynamically change prompting based on specific use case

Share and Copy buttons for feedback

<!-- image -->

<!-- image -->

Special UI elements for sources by type (e.g., video), related queries, etc.

Related queries

## @jxnlco @jxnlco

Once you start looking for interactions that help collect data, you'll see them everywhere

## Prompting: Reject Work

## Reject work.

- · Just like how we had to perform segmentations, I believe it's crucial to consider ways to enable the language model to reject work
- o Explore if few shotting works well "Here are examples of similar questions we cannot answer..."
- · Give it permission to say no, but follow up, and set expectations
- · If we model the success of this rejection system it's just another precision / recall trade off

<!-- image -->

<!-- image -->

## Monologues and Chain of Thought

I still see many companies underestimate the power of Chain of Thought

- · Chain of Thought is often a 10% bump in performance
- · It can often make the difference between something that is usable vs. unusable
- · If we wrapped Chain of Thought in either XML or in streaming, we can:
- · Build a dynamic UI that renders the Chain of Thought as separate data
- · Treat the Chain of Thought as some kind of loading interstitial too!

<!-- image -->

<!-- image -->

## Monologues and Chain of Thought

## Overview:

- · Leverage the monologue for multiple purposes
- · When dealing with lengthy contexts, the LLM may struggle with recall or fully process instructions
- · Try to prompt the model to reiterate relevant instructions and key text chunks before response generation
- · This is like training an intern who you'd naturally ask them to review and summarize important info
- · Consider including a 're -reading' prompt to improve reasoning

## Re-Reading Improves Reasoning in Large Language Models

Xiaohan Xu' Chongyang Tao? Tao Shen' Can Xu? Hongbo Xu' , Guodong Long Jian-guang Lou? 'Institute of Information Engineering; CAS, {xuxiaohan,hbxu}@iie.ac.cn

2Microsoft Corporation, {chotao, caxu, jlou}@microsoft.com

<!-- image -->

## @jxnlco @jxnlco

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Case study: Generating Quotes for SaaS Pricing

Overview: We built a capability focused on generating pricing quotes based on a call transcript

- · Detect that a pricing quote was being requested for a call
- · LLM Classifier was measured w/ recall
- · In the prompt, we included the entire one-hour transcript and the entire pricing document
- · By using monologues and Chain of Thought, we asked the LLM to:
- · Reiterate what variables determine the quotes
- · Reiterate relevant parts of the transcript
- · Reiterate parts of the pricing document that were relevant
- · As a result, the LLM reasoned what pricing options might be available before generating a response. With a single prompt, we were able to get our pricing questions answered without complex multi-stage reasoning
- · This allow us to make sure our follow ups were A+ and we had citations for our sales reps to verify the generated quotes. (We paid them to correct quotes, more data!)

<!-- image -->

Monologues before responses dramatically improve tonality and quality, which can be fine-tuned later without monologues.

<!-- image -->

## Monologues and Chain of Thought

Try to bake as much domain knowledge into these prompts, change prompts based on document types, be specific

You are an AI assistant tasked with answering queries based on given context.

Before generating a response, you must use &lt;monologue&gt;&lt;/monologue&gt; tags to reiterate the relevant instructions and the relevant text chunks involved in answering the query.

Here is the context you will be working with:

&lt;context&gt;

{{CONTEXT}}

&lt;/context&gt;

When answering a query, follow these steps:

- 1. Use &lt;monologue&gt;&lt;/monologue&gt; tags to:
- a. Reiterate the relevant instructions under &lt;relevant\_instructions&gt; tags
- b. Include the relevant parts of the context under &lt;relevant\_context&gt; tags
- 2. After the monologue, generate your response and enclose it in &lt;response&gt;&lt;/response&gt; tags.

## Monologues and Chain of Thought

Try to bake as much domain knowledge into these prompts, change prompts based on document types, be specific

You are an AI assistant tasked with answering queries based on given context.

Before generating a response, you must use &lt;monologue&gt;&lt;/monologue&gt; tags to reiterate the relevant instructions and the relevant text chunks involved in answering the query.

Here is the context you will be working with:

&lt;context&gt;

{{CONTEXT}}

&lt;/context&gt;

When answering a query, follow these steps:

- 1. Use &lt;monologue&gt;&lt;/monologue&gt; tags to:
- a. Reiterate the relevant instructions under &lt;relevant\_instructions&gt; tags
- b. Include the relevant parts of the context under &lt;relevant\_context&gt; tags
- 2. After the monologue, generate your response and enclose it in &lt;response&gt;&lt;/response&gt; tags.

<!-- image -->

Here is the query you need to answer:

&lt;query&gt;

{{QUERY}}

&lt;/query&gt;

Your output should follow this format:

&lt;monologue&gt;

&lt;relevant\_instructions&gt;

## [Reiterate the relevant instructions here]

&lt;/relevant\_instructions&gt;

&lt;relevant\_context&gt;

[Include the relevant parts of the context here]

&lt;/relevant\_context&gt;

&lt;/monologue&gt;

&lt;response&gt;

## [Your answer to the query goes here]

&lt;/response&gt;

Remember to always use the monologue tags before generating your response and ensure that your answer is based on the information provided in the context.

A single step is often not enough.

I would consider a validation pattern before going into full-blown multi-stage agents.

As our LLMS get more powerful, we're going to be able to do more and more within a single prompt. What might take an agent now might be possible with a single prompt in the future.

<!-- image -->

## Incorporating validators

- · In latency-insensitive applications, incorporating validators can help increase user trust and satisfaction in your product
- · Just use evals / tests within the production workflow
- · When we have components like reasoning, citations, and text chunks, we can utilize them in a secondary prompt:
- o Use an external system to evaluate whether the reasoning, citations, and generated response effectively answer the question
- o If they don't, the system provides detailed feedback on what's incorrect, unreasonable, or needs revision
- · Note!
- o These tests could be language models but it could also be unit tests or calls to external APIs

## @jxnlco @jxnlco

<!-- image -->

## Incorporating validators: Referencing Content without Hallucinations

## Problem:

- ▪ We wanted a language model to respond to emails with references to case studies and marketing material.
- ▪ However, we wanted to ensure that every single link is from the company namespace and that there were no hallucinations or invalid links since our links included UUIDs in the URL.

@jxnlco @jxnlco

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Incorporating validators: Referencing Content without Hallucinations

## Solution:

- · Our validator used a regular expression to find all urls
- · Checked domains for our allow list
- · We made a GET request to each URL to verify 200 status
- · If there were any issues, we would send an error and request regeneration
- · We initially had 4% failure rate, after 1 retry, it was 0%, after finetuning gpt-4o, 0% in a single pass

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

Even as of Feb 2025, Deep Research will include fake links to example.com/slug-1-2-3 when given the opportunity

## Food for thought: try this at work or in your own projects

<!-- image -->

## Work on food for thought from last few sessions

- · Generate synthetic data to test your system
- · Improve representations for each sub-task. Consider preparing triplet data sets, using Cohere re-rankers, or finetuning an embedding model (with sufficient data)
- · Implement user feedback mechanisms

<!-- image -->

<!-- image -->

## Questions to ask yourself

- · Am I being too subtle with collecting feedback on my product.
- · Could building better citations help me gain user trust and satisfaction?
- o Is there any way for me to leverage the citations to collect more relevancy data?
- · Could I implement better streaming, interstitials, and follow-up actions to make my application feel faster?
- · How can I better promote capabilities and reject other work
- · Can I include monologues and chains of thought to reiterate parts of the prompt and improve reasoning in my system.