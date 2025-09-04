# Chapter4 Slides

*Extracted from PDF slides using docling*

---

## jxnl.co

@jxnlco

## Systematically Improving RAG Applications

Session 4

Split: When to double down vs. when to fold

Jason Liu

## The RAG Flywheel

<!-- image -->

|                              |                                                                                                                                                                        | Step Description   |
|------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| 1                            | Start with a basic RAG system                                                                                                                                          | Step Description   |
| 2 Synthetic data generation  | Create synthetic questions to test the system's retrieval abilities                                                                                                    | Step Description   |
| 3 Fast evaluations           | Conduct quick, unit test-like evaluations to assess basic retrieval capabilities (e.g., precision, recall, mean reciprocal rank), and explain why each matters         | Step Description   |
| 4 Real-world data collection | Gather real user queries and interactions. Ensure feedback is aligned with business outcomes or correlated with important qualities that predict customer satisfaction | Step Description   |

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

## The RAG Flywheel

<!-- image -->

| Thesis: The principles we've applied Step                                               | Thesis: The principles we've applied Step                                                                                                                              | in search are highly relevant to what we want to do with RAG Description                |
|-----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 1 Initial                                                                               | Start with a basic RAG system setup                                                                                                                                    |                                                                                         |
| 2 Synthetic data generation                                                             | Create synthetic questions to test the system's retrieval abilities                                                                                                    |                                                                                         |
| 3 Fast evaluations                                                                      | Conduct quick, unit test-like evaluations to assess basic retrieval capabilities (e.g., precision, recall, mean reciprocal rank), and explain why each matters         |                                                                                         |
| 4 Real-world data collection                                                            | Gather real user queries and interactions. Ensure feedback is aligned with business outcomes or correlated with important qualities that predict customer satisfaction |                                                                                         |
| 5 Classification and analysis                                                           | Categorize and analyze user questions to identify patterns and gaps                                                                                                    |                                                                                         |
| 6 System improvements                                                                   | Based on analysis, make targeted improvements to the system                                                                                                            |                                                                                         |
| 7 Production monitoring                                                                 | Implement ongoing monitoring to track system performance                                                                                                               |                                                                                         |
| User feedback integration 8                                                             | Continuously incorporate user feedback into the system                                                                                                                 |                                                                                         |
| @jxnlco @jxnlco maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook | @jxnlco @jxnlco maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook                                                                                | @jxnlco @jxnlco maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook |

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

## Example: Segmentation in marketing

How segmentation supports decision making

How segmentation supports decision making

Two types of segments

Two types of segments

Food for thought for this session

Food for thought for this session

Sneak peak for rest of course

Sneak peak for rest of course

## Example: Segmentation in marketing

## Situation:

- · You sell a consumer product and run a marketing campaign to boost sales

## Complication:

- · As a result of your efforts, you discover that there is an 80% boost in sales…but you don't know what is causing the boost
- · Alternatively, you could also have an 80% drop in sales…and you don't know what is causing the drop

## Approach:

- · You dig through your sales data, looking across different customer segments and realize that 60% of the sales increase (or drop) are coming from Segment 1: 30 -45-year-old women living in the Midwest

## Impact:

- · With this information, your team can decide:
- · If this is an audience that we want to invest more in
- · How better to target this audience (e.g., not running Super Bowl ads)

<!-- image -->

## Example: Segmentation in marketing

## Situation:

- · You sell a consumer product and run a marketing campaign to boost sales

## Complication:

- · As a result of your efforts, you discover that there is an 80% boost in sales…but you don't know what is causing the boost
- · Alternatively, you could also have an 80% drop in sales…and you don't know what is causing the drop

## Approach:

- · You dig through your sales data, looking across different customer segments and realize that 60% of the sales increase (or drop) are coming from Segment 1: 30 -45-year-old women living in the Midwest

## Impact:

- · With this information, your team can decide:
- · If this is an audience that we want to invest more in
- · How better to target this audience (e.g., not running Super Bowl ads)

<!-- image -->

If you can properly identify the demographics and psychographics of the inputs of your system, your team will have multiple levers to experiment with and allocate resources and start to explore vs. exploit our system

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Demographics

The quantifiable characteristics (observable traits) of a given population:

- · Role
- · Organization ID
- · Cohort
- · Life stage

•

...

<!-- image -->

## Demographics

The quantifiable characteristics (observable traits) of a given population:

- · Role
- · Organization ID
- · Cohort
- · Life stage

•

...

<!-- image -->

## Psychographics

The psychological aspects of consumer/user behavior and preferences:

- · Attitudes
- · Values
- · Interests
- · Writing style
- · Preferred response style

```
{ }
```

```
"query": "What was the difference between the 2022 and 2023 budgets?", "average_similarity": 0.6, "average_cohere_score": 0.8, "customer_rating": 1, "query_types": [ "TIME_FILTER", "MULTIPLE_QUERIES", "FINANCIAL_QUERY" ]
```

```
@jxnlco maven.com/applied-llms/rag-playbook
```

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

Example: Segmentation in marketing

Example: Segmentation in marketing

## How segmentation supports decision making

Two types of segments

Two types of segments

Food for thought for this session

Food for thought for this session

Sneak peak for rest of course

Sneak peak for rest of course

## What would we do with our segments?

<!-- image -->

<!-- image -->

## What would we do with our segments?

<!-- image -->

<!-- image -->

## What would we do with our segments?

<!-- image -->

## Key takeaway:

## How do we do this?

If we can label query types we can build specialized systems to maximize impact or p(success)

- · Leveraging clustering methods and few shot classifiers, we can domain model our way into building prompts that can classify and segment queries
- · Then we can batch offline and also monitor online in production

## What would we do with our segments?

<!-- image -->

## Key takeaway:

## How do we do this?

If we can label query types we can build specialized systems to maximize impact or p(success)

## @jxnlco @jxnlco

- · Leveraging clustering methods and few shot classifiers, we can domain model our way into building prompts that can classify and segment queries
- · Then we can batch offline and also monitor online in production

## The real challenge:

- · Estimate Impact (User Research)
- · Measuring Likelihood of success (Collecting User feedback)
- · Controlling Query Volume

## User feedback as a proxy

## You can start to gather user feedback early on*

<!-- image -->

* We don't recommend a 5-star system

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## User feedback as a proxy

## You can start to gather user feedback early on*

<!-- image -->

* We don't recommend a 5-star system

Make sure users understand what the buttons correspond to through your copy

How did we do? Uncorrelated with customer satisfaction

<!-- image -->

## Did we answer your question?

Highly correlated with satisfaction and correctness maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## User feedback as a proxy

## You can start to gather user feedback early on*

<!-- image -->

* We don't recommend a 5-star system

Make sure users understand what the buttons correspond to through your copy

How did we do? Uncorrelated with customer satisfaction

## Did we answer your question?

Highly correlated with satisfaction and correctness

Its important to do both UX to collect feedback but also to do user research to understand the impact of questions

<!-- image -->

## You can also allow users to:

- · Rate / Delete sources
- · Copy Snippets
- · Share
- · Publish
- · Save
- · Etc.

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## What do we about different user segments?

Above average

Below average

Query  volume

## Maintain

Below average

Above average

- • Continuously monitor and review performance metrics to ensure quality

- • If this section very high, consider trying to break down this segment even farther

User satisfaction

<!-- image -->

## What do we about different user segments?

## Above average

Below average

## Query  volume

## High ROI

## Maintain

Below average

Above average

- • Continuously monitor and review performance metrics to ensure quality

- • If this section very high, consider trying to break down this segment even farther

- • Promote or highlight capabilities to users!

- • Identify if high impact w/ user research

- • Identify if sampling bias (Example)

- • Experiment with UI changes to boost usage and visibility

User satisfaction

<!-- image -->

## What do we about different user segments?

## Above average

Below average

## Query  volume

## Low ROI

## High ROI

## Maintain

Below average

Above average

- • Continuously monitor and review performance metrics to ensure quality

- • If this section very high, consider trying to break down this segment even farther

- • Perform a cost-benefit analysis to determine the value of continued efforts

- • Adjust the UI to set clear expectations

- • Consider phasing out or overhauling if not essential

- • Promote or highlight capabilities to users!

- • Identify if high impact w/ user research

- • Identify if sampling bias (Example)

- • Experiment with UI changes to boost usage and visibility

User satisfaction

<!-- image -->

## What do we about different user segments?

## Above average

## Danger Zone

- · Conduct in-depth user surveys and focus groups to identify pain points
- · Prioritize and implement targeted improvements
- · Try to identify subsegments that perform better
- · Is it 20% of queries fail or each query has a 20% success rate?

## Low ROI

- · Perform a cost-benefit analysis to determine the value of continued efforts
- · Adjust the UI to set clear expectations
- · Consider phasing out or overhauling if not essential

Below average

## Query  volume

Below average

<!-- image -->

## Maintain

- · Continuously monitor and review performance metrics to ensure quality
- · If this section very high, consider trying to break down this segment even farther

## High ROI

- · Promote or highlight capabilities to users!
- · Identify if high impact w/ user research
- · Identify if sampling bias (Example)
- · Experiment with UI changes to boost usage and visibility

Above average

User satisfaction

## Case study: Project Management for Construction Company

Personal anecdote about understanding user behavior and satisfaction

## Situation

- · Product team hypothesized that scheduling was an important use case for the RAG app
- · However, the data showed that users were using the RAG app primarily for document search instead
- · &gt;50% queries were document search with ~70% user satisfaction

<!-- image -->

## Case study: Project Management for Construction Company

Personal anecdote about understanding user behavior and satisfaction

## Situation

## Complication

- · Product team hypothesized that scheduling was an important use case for the RAG app
- · However, the data showed that users were using the RAG app primarily for document search instead
- · &gt;50% queries were document search with ~70% user satisfaction
- · By plotting query segments and satisfaction over time, team discovered that:
- · New users started with scheduling questions but had low satisfaction
- · As a result, users shifted to document searches (often related to scheduling)
- · High document search satisfaction masked poor schedule search performance

<!-- image -->

## Case study: Project Management for Construction Company

Personal anecdote about understanding user behavior and satisfaction

## Situation

## Complication

## Approach

- · Product team hypothesized that scheduling was an important use case for the RAG app
- · However, the data showed that users were using the RAG app primarily for document search instead
- · &gt;50% queries were document search with ~70% user satisfaction
- · By plotting query segments and satisfaction over time, team discovered that:
- · New users started with scheduling questions but had low satisfaction
- · As a result, users shifted to document searches (often related to scheduling)
- · High document search satisfaction masked poor schedule search performance
- · Eng team shifted focus to systematically improve schedule search to better understand queries about
- · Due dates
- · Payment dates
- · All parties signed off by due date
- · Team communicated with clients about new schedule searching capabilities

## Case study: Project Management for Construction Company

Personal anecdote about understanding user behavior and satisfaction

## Situation

## Complication

## Approach

- · Product team hypothesized that scheduling was an important use case for the RAG app
- · However, the data showed that users were using the RAG app primarily for document search instead
- · &gt;50% queries were document search with ~70% user satisfaction
- · By plotting query segments and satisfaction over time, team discovered that:
- · New users started with scheduling questions but had low satisfaction
- · As a result, users shifted to document searches (often related to scheduling)
- · High document search satisfaction masked poor schedule search performance
- · Eng team shifted focus to systematically improve schedule search to better understand queries about
- · Due dates
- · Payment dates
- · All parties signed off by due date
- · Team communicated with clients about new schedule searching capabilities

## Key takeaway:

- · There may be key areas of improvement that are obfuscated by summary statistics (e.g., overall user satisfaction). Don't pat yourself on the back just yet
- · Users are savvy and may change their behavior based on the capabilities of your product. Additional research (e.g., focus groups) and analysis are essential to discover why

## Impact

[Next page]

## Case study: Project Management for Construction Company

Personal anecdote about understanding user behavior and satisfaction

<!-- image -->

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

<!-- image -->

## Lesson:

Summary statistics are not enough… and sometimes may fool you

## It's not going to 'just work because it's AI'

## What RAG actually is:

<!-- image -->

maven.com/applied-llms/rag-playbook

## It's not going to 'just work because it's AI'

## What RAG actually is:

<!-- image -->

## Key takeaways

- · We will need to revert to good old machine learning and data science
- · We need to conduct exploratory data analysis to find segments worth pursing
- · We need to:
- o Work with domain experts to do feature engineering
- o Identify specific candidate indices using additional metadata that improves performance in high impact segments

maven.com/applied-llms/rag-playbook

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

Two types of segments

Two types of segments

## Overview

Lack of inventory

Lack of inventory

Lack of capabilities

Lack of capabilities

Sneak peak for rest of course

Sneak peak for rest of course

Food for thought for this session

Food for thought for this session

## How to distinguish between the two types of issue segments

| Problems                   | Lack of inventory                                                                                                                                  |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| Origin of issue            | • Limited content in knowledge base                                                                                                                |
| How to address this issue` | Expand inventory: • Expand the corpus of information • Improve ingestion and data connectors • Create more focused sub-systems for specific topics |

## How to distinguish between the two types of issue segments

| Problems                   | Lack of inventory                                                                                                                                  | Lack of capabilities                                                                                                                                                                                                                                                                                                 |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Origin of issue            | • Limited content in knowledge base                                                                                                                | • The system's functional abilities • Metadata may exist but not structured Anything that is not an inventory issue…                                                                                                                                                                                                 |
| How to address this issue` | Expand inventory: • Expand the corpus of information • Improve ingestion and data connectors • Create more focused sub-systems for specific topics | Technical improvements: • Enhance system's ability to understand • Extract additional meta data (e.g., project due date index from proposal docs, map calendar year based on industry) • Add new search features based on additional data • Create a new search index (e.g., CRM index, email index, calendar index) |

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## How to distinguish between the two types of issue segments

| Problems                   | Lack of inventory                                                                                                                                  | Lack of capabilities                                                                                                                                                                                                                                                                                                 |
|----------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Origin of issue            | • Limited content in knowledge base                                                                                                                | • The system's functional abilities • Metadata may exist but not structured Anything that is not an inventory issue…                                                                                                                                                                                                 |
| How to address this issue` | Expand inventory: • Expand the corpus of information • Improve ingestion and data connectors • Create more focused sub-systems for specific topics | Technical improvements: • Enhance system's ability to understand • Extract additional meta data (e.g., project due date index from proposal docs, map calendar year based on industry) • Add new search features based on additional data • Create a new search index (e.g., CRM index, email index, calendar index) |

## @jxnlco @jxnlco

## Why is this important?

- · By categorizing user queries into segments and identifying what is required to address them, developers can more effectively:
- · Prioritize system improvements more effectively
- · Identify gaps in knowledge and functionality
- · Develop specialized subsystems or features for specific use cases
- · Improve overall user experience by ensuring the system can handle a wide range of query types effectively

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

Two types of segments

Two types of segments

Overview

Overview

## Lack of inventory

Lack of capabilities

Lack of capabilities

Sneak peak for rest of course

Sneak peak for rest of course

Food for thought for this session

Food for thought for this session

## Lack of inventory examples

<!-- image -->

| Company   | Problem                                                                                                                                                | Solution                                                |
|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------|
| Text      | User query : 'batteries' or 'televisions' Early Amazon: No results for batteries or televisions, only results for books about batteries or televisions | • Expand inventory to include batteries and televisions |

<!-- image -->

## Lack of inventory examples

<!-- image -->

<!-- image -->

| Company                                                           | Problem                                                                                                                                                  | Solution    |
|-------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|-------------|
|                                                                   | User query : 'batteries' or 'televisions' Early Amazon: No results for batteries or televisions, only results for books about batteries or televisions • | Text Expand |
| User query: Spanish telenovelas Netflix: Limited relevant results | • Produce more TV in different languages for different demographics • Improve subtitles                                                                  | Text        |

<!-- image -->

## Lack of inventory examples

<!-- image -->

<!-- image -->

<!-- image -->

| Company   | Problem                                                                                                                                                | Solution                                                                                                                                                       |
|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|           | User query : 'batteries' or 'televisions' Early Amazon: No results for batteries or televisions, only results for books about batteries or televisions | Text • Expand                                                                                                                                                  |
|           | User query: Spanish telenovelas relevant results • Produce more TV in different languages different demographics • Improve subtitles                   | Text                                                                                                                                                           |
| Text      | User query : 'Greek restaurants near me' Doordash: Limited results                                                                                     | • Reach out to more Greek restaurants (in specific zip codes) and get more Greek restaurants onto the platform • Buy resturants iPads to process online orders |

<!-- image -->

## Proxies for poor inventory

- · Low cosine similarities as a proxy for low relevancy
- · Lexical Search returns 0 results
- · LLMs not answering questions due to missing data
- · LLMs not citing any chunks included in context when returning answers
- · Make sure logging
- · Product issues:
- · Problems with data pipeline and data improperly ingested
- · Broken configurations
- · Customers are not providing data which they said they would

<!-- image -->

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

Two types of segments

Two types of segments

Overview

Overview

Lack of inventory

Lack of inventory

## Lack of capabilities

Food for thought for this session

Sneak peak for rest of course

Sneak peak for rest of course

Food for thought for this session

## Lack of capabilities examples

<!-- image -->

| Company   | Problem                                                                                   | Solution                                                                                                               |
|-----------|-------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Text      | User query : 'Affordable heels with less than 3 - inch heel' Amazon: Few relevant results | • Identify additional feature meta-data and join on existing data • Filter on specific features based on product types |

## Lack of capabilities examples

<!-- image -->

<!-- image -->

| Company                            | Problem                                                                                                                                                    | Solution                                          |
|------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| Text User query inch heel' Amazon: | heels with less than 3 - results • Identify additional feature meta-data and join on existing data • Filter on specific features based on product types    | : 'Affordable                                     |
|                                    | nominated films' results with movie titles or • Acquire additional meta-data for existing catalogue • Join on these datasets to better answer user queries | Text User query : 'Oscar - Early Netflix: Returns |

## Lack of capabilities examples

<!-- image -->

<!-- image -->

<!-- image -->

| Company   | Problem                                                                                                                  | Solution                                                                                                                                                                               |
|-----------|--------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|           | User query : 'Affordable heels with less than 3 - inch heel' Amazon: Few relevant results                                | Text • Identify                                                                                                                                                                        |
| Text      | User query : 'Oscar - nominated films' Early Netflix: Returns results with movie titles characters which include 'Oscar' | or • Acquire additional meta-data for existing • Join on these datasets to better answer queries                                                                                       |
| Text      | User query : 'Chinese food' (it's after 9pm) Doordash: Limited conversion                                                | • Figure out how to get up-to-date availability data • Add an 'Open Now' button to specify restaurants • New features (e.g., allow users to schedule orders for when restaurants open) |

<!-- image -->

## Common (but fixable!) capabilities issues

## Problem

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

| Datetime filter for 'what happened recently' or 'what's the latest on…'   |
|---------------------------------------------------------------------------|
| Comparisons                                                               |
| Filters for Tabular Data in PDF                                           |
| Specific filters for stock tickers (before a document search)             |
| Understand document metadata                                              |

<!-- image -->

## Common (but fixable!) capabilities issues

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

<!-- image -->

| Problem         | Solution                                                                |                                                                                                                                                                                                                                       |
|-----------------|-------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|                 | Datetime filter for 'what happened recently' or 'what's the latest on…' | • 'Recent' or 'Latest' is contextual based on the query, use few shots o 'Latest' emails != "Recent' physics research                                                                                                                 |
|                 | Comparisons                                                             | • Requires multiple search queries and a comparison between the two sets of results                                                                                                                                                   |
|                 | Filters for Tabular Data in PDF                                         | • Users may want to answer questions over tables using SQL-like behavior • Users may want to search for rows or columns in large data tables like a spec sheet                                                                        |
|                 | Specific filters for stock tickers (before a document search)           | • Find specific ticket, quarter, document type to limit search and generate better results                                                                                                                                            |
| @jxnlco @jxnlco | Understand document metadata                                            | maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook • Store meta data (e.g., modification history to understand who last modified the procurement form) • Find me contracts that are unsigned past their due date |

## Lack of capabilities examples

## How to fix a lack of capabilities

- · Query routing: Run multiple searches in parallel and combine information
- · Extract metadata: Pre-process data and build new indices to search against, used to filter and sort queries
- · Long context: Conditionally use long context models rather than RAG when answers are found in short documents rather than many chunks
- · Generation prompt: Based on the document types change how we generate or render responses

<!-- image -->

## Call out:

Topic Modeling is only a tool to come up with explicit Classifications

## Exploratory Data analysis

- · Test a variety of different hypotheses by running experiments
- · Determine new capabilities and user requirements: Work with domain experts, clustering methods and few shot classifiers to find and propose 'segments':

## Examples:

-  Searching for contact information (e.g., render contact cards when the query contains a person)
-  Searching across files (e.g., determine if a file should be displayed or if audio data should be summarized)
-  Searching across time (e.g., display a clock widget for time-related queries)

<!-- image -->

## Classification example

<!-- image -->

<!-- image -->

## Consider classifying on :

- · Question types
- · Context recovered
- · Search indices hit
- · Format type and responses returned

maven.com/applied-llms/rag-playbook

## Classification example

<!-- image -->

@jxnlco @jxnlco

For each job type, the percentage of relevant conversations with Claude is shown in orange compared to the percentage of workers in the U.S. economy with that job type (from the U.S. Department of Labor's O*NET categories) in gray.

## Anthropic recently also did data analysis on their queries to uncover segments

- · Computer and mathematical

https://www.anthropic.com/n ews/the-anthropiceconomic-index maven.com/applied-llms/rag-playbook

51 maven.com/applied-llms/rag-playbook maven.com/applied-llms/ragplaybook

## Exploration and Monitoring

## Title If you don't have user data…

- · A priori zero-shot or few-shot potential topics and capabilities users may have
- · Set up monitoring system as you roll out a production system

<!-- image -->

## Exploration and Monitoring

## Title If you don't have user data…

- · A priori zero-shot or few-shot potential topics and capabilities users may have
- · Set up monitoring system as you roll out a production system

<!-- image -->

## If you do have user data…

- · Run topic modeling and clustering
- · Present topics
- · Identify 5-10 example queries for both satisfied and unsatisfied clusters
- · Collaborate with domain experts and user researchers to analyze clusters

## Uncovered topic example: customer support

Through topic modeling, you discover that queries about customer support are frequent:

## Positive examples

Show me the last 10 support tickets

First 10 customer support tickets about battery life complaints

Jason Liu's support tickets maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Uncovered topic example: customer support

Through topic modeling, you discover that queries about customer support are frequent:

| Positive examples                                                                           | Negative examples                                                   |
|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Show me the last 10 support tickets                                                         | Is Jason a good customer service rep?                               |
| First 10 customer support tickets about battery life complaints Jason Liu's support tickets | Who is likely to churn and why? What do people complain about most? |

## Uncovered topic example: customer support

Through topic modeling, you discover that queries about customer support are frequent:

| Positive examples                                                                           | Negative examples                                                   |
|---------------------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Show me the last 10 support tickets                                                         | Is Jason a good customer service rep?                               |
| First 10 customer support tickets about battery life complaints Jason Liu's support tickets | Who is likely to churn and why? What do people complain about most? |

## Current performance:

- · No issues: Finding support tickets
- · Significant issues: Reporting on Customer Service Rep Metrics
- · Major challenge: Churn prediction is nearly impossible to reason about for an LLM

## Potential solutions:

- · Render support tickets in UI
- · Implement a tool that renders customer support rep metrics
- · Build a model to do sentiment analysis on individual customer service threads or topics

maven.com/applied-llms/rag-playbook maven.com/applied-llms/rag-playbook

## Call out:

Make sure to convert offline analysis to online analysis too

<!-- image -->

## Why monitor topics online?

Automation Paradox: Automation saves you time, but issues will multiply if left unchecked, sampling production is the easiest way to understand what is going on.

<!-- image -->

## Why monitor topics online?

Automation Paradox: Automation saves you time, but issues will multiply if left unchecked, sampling production is the easiest way to understand what is going on.

## Instructions for Online Monitoring

- · Establish topic clusters / classifications you want to monitor and check against for when new topics emerge
- · Make sure to have an 'Other' category and monitor how this fluctuates as new customers are onboarded
- · Detect changes to the system after any product changes or new users
- · Build Dashboards:
- · Track Distributions of query types over time
- · Track % Other to detect drift in your systems
- · Track Satisfaction and Volume per Query Type
- · Track Average Relevance per Query Type
- · Track Metrics across Cohorts and Organizations
- · Conduct exploratory analysis when systems changes in an unexpected way

## Why monitor topics online?

After you attract new users, these users may use the app differently relative to your existing users because of

- · Demographics
- · Psychographics

You can better detect and understand why satisfaction may drift.

## For example:

- · New users ask different kinds of questions that we need different inventory or capabilities
- · Seasonality, etc.

## Concept Drift Visualization across Multiple Dimensions

<!-- image -->

## Session 4: Key takeaways

- Gain a holistic view of system performance and user engagement A
- B
- Identify specific areas (e.g., users, content, features) that need the most attention
- Tailor your interventions and improvements to address the most impactful issues C
- Proactively monitor your system to detect evolving user needs and behaviors D

<!-- image -->

<!-- image -->

<!-- image -->

The goal is not only to detect concept drift, but also to understand its nuances across all aspects of your system.

This multi-dimensional approach enables more targeted and effective strategies to maintaining and improving your RAG system

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

Two types of segments

Two types of segments

## Food for thought for this session

Sneak peak for rest of course

Sneak peak for rest of course

## Food for thought: try this at work or in your own projects

<!-- image -->

Analyze User Queries: Perform topic modeling or batch classification to identify inventory or capability issues

<!-- image -->

<!-- image -->

Evaluate answer quality: Identify examples of good and bad responses to guide improvements. Use these examples to guide improvements in the system's response quality.

## Implement audit feedback mechanisms:

- · Implement user feedback UI
- · Assess how often users use the thumbs-up and thumbs-down buttons for feedback
- · Analyze if the feedback mechanism is effective and consider changes if necessary (e.g., larger buttons, repositioning).

<!-- image -->

<!-- image -->

Make step-wise improvements: Discuss with your team where to make improvements

- · What Metadata is missing?
- · What filters are missing?
- · What indices are missing?

<!-- image -->

<!-- image -->

Why does segmentation matter

Why does segmentation matter

Two types of segments

Two types of segments

Food for thought for this session

Food for thought for this session

## Sneak peak for rest of course

## Sneak peek for rest of course

- · Focus for last session:
- · The Art of RAG UX: Subtle and obvious ways to build confidence and trust in your RAG app
- · Focus for this session:
- · Learned to about segmentation and how to distinguish between inventory and capabilities issues and how to approach solving them. We will need to invest a lot of time in extending our capabilities in specific rather than general ways (e.g., solving problems locally within certain segments)
- · Established the importance of production / online monitoring

## Focus for next 2 sessions:

- · Focus on details of what kinds of capabilities to think about and what to watch out for:
- · Session 5: Map - Structured extraction and multimodality
- · Session 6: Apply - Routing queries and testing router accuracy