---
title: Week 4 - Office Hour 2
date: '2024-06-12'
cohort: 3
week: 4
session: 2
type: Office Hour
transcript: ../GMT20250612-174842_Recording.transcript.vtt
description: AI report generation, data visualization, and unstructured feedback data analysis systems
topics:
  - Dynamic Data Visualization
  - Professional Report Styling
  - Unstructured Customer Feedback
  - Fast Classifier Development
  - Tool-based vs Semantic Search
  - Cura Project Development
  - Future Course Content
  - Report Generation Enhancement
---

# Week 4, Office Hour 2 (June 12)

Study Notes:

I hosted another office hours session focused on AI report generation, data visualization, and handling unstructured feedback data. Here are my thoughts on creating effective AI-generated reports, implementing dynamic visualizations, and building systems that can analyze customer feedback at scale.

## How should I approach dynamic data visualization in AI-generated reports?
When creating AI-generated reports with dynamic visualizations, there are several approaches to consider depending on your specific needs.

For deep research-style reports (like those from Gemini, Claude, or OpenAI), the LLM typically decides on a set of subtasks and executes them sequentially. These reports often don't include charts or visualizations by default, though OpenAI's deep research does incorporate images.

For more structured reports with visualizations, I see three main approaches:

1. Post-hoc image addition: You can have the LLM identify places where supplementary images would enhance the text, then add them afterward.
1. Image citations during research: Treat images as another citation source that the LLM can reference while generating text. For example, with a client yesterday, the LLM decided to include an org chart in a leadership report because it had access to an org chart JPEG file during generation.
1. Mermaid diagrams: These are particularly useful for creating dynamic visualizations directly in Markdown. The key challenge is validation - if Claude generates an incorrect Mermaid diagram, it simply fails to render. You need a validation loop or external server to check the diagram code, report errors, and iterate to fix them.

For standard data visualizations, most companies use JavaScript libraries like Recharts, which allow you to pass data as props and generate visualizations.

The approach depends on whether your report format is flexible or fixed. If fixed, each header might have its own RAG workflow - for example, every competitor analysis might need a leadership team section, which triggers a subtask to find the leadership team of the target company.

***Key Takeaway:*** The most effective approach I've found is creating an abundance of visualization options during generation and letting users delete what they don't want. This creates a natural feedback loop where you can track which visualizations users keep versus delete, building a dataset that improves future recommendations.

## How can we handle styling challenges in professional reports?
One of the biggest challenges in AI report generation is matching the exact styling expectations of professional reports. I work with companies that sell to consultants like McKinsey, and the hardest part isn't generating the content - it's making the slides and plots look exactly like McKinsey-branded material.

While it's easy to plug in matplotlib or Recharts, it's extremely difficult to match the precise styling requirements of professional consulting firms. Some clients are literally saying, "We're not going to pay you any of that $80,000 unless you can make it look like we actually made this."

These firms often use specialized software from the early 2000s for plot generation, with very specific requirements about legend shapes, marker styles (X's versus T's), and other formatting details. The styling is so challenging that we're considering using computer vision to train systems to use PowerPoint and implement styling changes based on feedback comments.

I believe there's a significant market opportunity here - you could easily sell software that generates McKinsey-style plots for $100,000 to an analyst team. The last 5% of styling is what makes the difference between something that looks AI-generated versus professionally produced.

***Key Takeaway:*** The styling challenge represents a major opportunity for AI tools that can match the exact visual requirements of professional consulting firms. The technical content generation is often easier than matching the precise styling expectations that make reports look professionally produced.

## How should I approach analyzing unstructured customer feedback data?
For a project like Netflix's customer feedback analysis, where you're collecting unstructured data through a "report a problem" feature, I recommend a hybrid approach combining semantic search with structured analysis.

First, consider doing hierarchical clustering to build a taxonomy of error categories. This gives you a structured way to analyze the data beyond just semantic search. By tagging all feedback with these hierarchical categories, you can provide accurate counts and faceted navigation.

When a user asks "What are members saying about Seinfeld's aspect ratio?", you might return 10-20 semantically relevant results, but also show facets like "200 comments in this category, 80 in that category" to help them understand the distribution of issues.

This approach allows users to traverse the data in interesting ways - they might start with audio issues, discover that 20% of complaints are about Seinfeld, then dig into which season has the most problems. The goal is giving users a portfolio of tools to explore the hierarchy rather than just semantic search alone.

For quantitative questions like "How many audio sync issues were reported in Brazil last month?", you need structured data. The LLM will hallucinate counts if you rely solely on semantic search. By building lightweight classifiers for common issues, you can provide accurate counts while still allowing semantic exploration of the unstructured text.

I worked with a company called Interpret that built something similar - a chatbot that could talk to customer feedback and give realistic counts by combining semantic understanding with structured analysis.

***Key Takeaway:*** The most effective approach combines semantic search with structured analysis through hierarchical clustering and classification. This gives users both the flexibility to explore feedback semantically and the accuracy of structured data for quantitative questions.

## What's the best way to build fast classifiers for unstructured data?
When you need to quickly classify unstructured data, there are several approaches depending on your requirements.

One approach is using embedding-based classification. As Jan mentioned, OpenAI's documentation describes a simple technique where you embed category descriptions and then classify items by finding the closest category embedding. This works well for straightforward classification tasks and is extremely fast to implement.

In my previous work, we used a matrix-based approach where we'd embed all products in a matrix, then learn another matrix to multiply by the product embeddings whenever we needed to build a classifier. This allowed us to label about 1,000 examples, learn the weights, and then multiply the entire product space by that vector to get predictions for every product. It was very fast but typically achieved around 85% accuracy.

For Netflix's feedback analysis, you might want to combine pre-defined categories from domain experts with data-driven clusters discovered through analysis. There will be common issues like rendering problems or audio sync issues that domain experts can define, plus a longer tail of soft clusters that emerge from the data.

The key is building a system that can quickly create and apply these classifiers as new issues emerge. When a new feature launches, you want to detect feedback about it immediately, even if it wasn't in your training data.

***Key Takeaway:*** Fast classifier development is essential for responsive feedback analysis. Combining embedding-based approaches with domain expertise allows you to quickly identify both known issues and emerging patterns in user feedback.

## How should we think about tool-based approaches versus semantic search?
I believe we're moving toward a world where many RAG applications will use tool-based approaches rather than pure semantic search, especially for structured data.

In the coming weeks, we'll have talks from teams building coding agents that use a portfolio of tools rather than semantic search. Their thesis is that for structured data, the right way to prepare context isn't one semantic search request, but an agent using multiple tools to build context incrementally.

Think about how you debug an error message - you see the error came from a specific file, so you load that file, then you find the function causing the issue, load that file, and traverse the file tree building context before solving the problem. Coding agents are implementing this approach rather than embedding all code.

You can implement this with simple tools like "ls" (list files), "read_file", and "grep". The agent uses these tools to navigate the data, building context as it goes. This approach might cost more at query time but requires less preprocessing of data.

I'm curious if this approach would work for traversing complex documents like 1,000-page PDFs. Instead of embedding everything, you could provide tools like "list_table_of_contents", "grep", "show_page", and "show_page_as_image". The agent could navigate the document naturally, finding references and following them just as a human would.

***Key Takeaway:*** Semantic search is most valuable when the producer and consumer of data don't share vocabulary. For structured data or documents with clear organization, a tool-based approach that mimics human navigation may be more effective and require less preprocessing.

## What are you working on with your Cura project?
We're making progress on building out Cura, which is an open-source project (not quite a product yet) focused on analyzing conversation data. In the next few days, we'll be benchmarking it on about a thousand conversations to see what patterns we discover.

The core of the project involves hierarchical clustering, explaining clusters, and generating names for these clusters. We're planning to download every open-source chat conversation dataset and run our analysis on it to see what we find.

My philosophy with any product I build is that it should function as a sensor that generates data. I want to "trick" users into labeling data for me. If I don't know which chart type works best, I'll generate three options and ask users to delete the ones they don't want. My messaging is that it's important for them to review the data, but I'm actually collecting valuable feedback on what visualizations work best.

We apply the same approach to citations in paragraphs - users can mouse over citations to see the source data and delete or regenerate citations they don't trust. This creates a feedback loop that continuously improves the system.

***Key Takeaway:*** Building products that function as data collection sensors is a powerful approach. By giving users options and tracking their choices, you can gather valuable feedback that improves your system while providing a better user experience.

## What upcoming content are you excited about in the course?
I'm particularly excited about the second half of the course where we'll dive deeper into data analysis and explore the portfolio of tools approach.

In the coming weeks, we'll have talks from Reducto, one of the best PDF parsing libraries available right now. They have contracts with companies like Vanta and government agencies and have achieved impressive results.

We'll also be inviting teams building coding agents, including the Augment team and the Klein team. These companies are focusing less on RAG with semantic search and more on RAG using a portfolio of tools. Their thesis is that for structured data like code, the right approach isn't one semantic search request but an agent using multiple tools to build context.

Beyond the course, I'm organizing a speaker series with guests from OpenAI's memory team and possibly Claude Code. My goal is to bring in the most interesting speakers in the field to share their insights.

***Key Takeaway:*** The future of RAG systems, especially for structured data like code, may involve less semantic search and more tool-based approaches where agents navigate information using a portfolio of tools to build context incrementally.

______________________________________________________________________

FAQs

## How can I create dynamic charts and tables for high-value reports?

There are several approaches to creating dynamic visualizations in reports. You can use JavaScript libraries like Rechart for data visualizations, where you pass in data and choose between different chart types (bar charts, pie charts, etc.). For diagram generation, Mermaid is a popular option, though you'll need a validation system to catch and fix any errors in the generated code. For more complex reports, you might need to consider the specific styling requirements of your audience and potentially use specialized tools that match their expected formats.

## What's an effective approach to handling multiple visualization options in reports?

A powerful technique is to generate multiple visualization options and let users delete what they don't want. By providing an abundance of charts and visualizations with a simple delete function, you allow users to filter what works best for their needs. This approach has the added benefit of generating valuable feedback data - by tracking which visualizations users keep versus delete, you can improve future recommendations and learn which visualization types work best for specific data scenarios.

## How can I handle citations in reports?

Similar to visualizations, you can implement a system where citations are included with mouse-over functionality to show the source. Users can delete citations they don't find valuable and regenerate them if needed. This creates an interactive review process that improves the quality of the final report while collecting useful preference data.

## What are the challenges with styling reports for specific clients?

One of the biggest challenges is matching the exact styling requirements of specific organizations, especially consulting firms that have distinctive visual branding. Standard libraries like Rechart or Matplotlib can generate visualizations, but they often don't match the precise styling (legend shapes, specific colors, font treatments) that clients expect in high-value reports. This "last 5%" of styling is what makes reports not look AI-generated and can be crucial for client acceptance.

## How can I analyze unstructured feedback data effectively?

For analyzing unstructured feedback (like customer comments or issue reports), consider implementing a hierarchical clustering approach to identify patterns and create a taxonomy of categories. This allows you to provide both semantic search capabilities and accurate counts of issues by category. The most effective systems combine semantic search with structured filtering, allowing users to traverse the data in multiple ways - searching for specific issues while also seeing the distribution of issues across different dimensions (products, regions, time periods, etc.).

## What's the difference between deep research reports and structured reports?

Deep research reports are more freeform, where an LLM decides on subtasks and conducts research independently. These often don't include charts or visualizations but focus on comprehensive text analysis. Structured reports, on the other hand, follow specific templates with predefined sections, potentially including visualizations, citations, and formatted data. Both have their place depending on the use case and audience requirements.

## Should I use semantic search or direct tool access for document navigation?

It depends on your document structure. If you're working with highly structured documents where specific terminology is consistent (like technical manuals or legal documents), a portfolio of simple tools (grep, read file, list files) can be more efficient than semantic search. This "tool-based traversal" approach can be particularly effective for large documents with clear organization, allowing an agent to navigate through content using direct commands rather than embedding the entire document.

## How can I quickly build classifiers for new categories in feedback data?

For rapid classifier development, you can use embedding-based approaches where you embed category descriptions and then match new items to the closest category embedding. Another approach is to use a small set of labeled examples to train a lightweight classifier. The key is having a system to validate the accuracy of these classifiers and being able to quickly deploy them to generate counts and insights from your data.
