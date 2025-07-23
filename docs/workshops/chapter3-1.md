---
title: "Chapter 3.1: Feedback Collection"
description: Building feedback flywheels into your RAG applications
author: Jason Liu
---

# Feedback Collection: Building Your Improvement Flywheel

!!! abstract "Chapter Overview"

```
This chapter explores the essential role of feedback collection in RAG systems, introducing the concept of a feedback flywheel for systematic improvement. You'll learn practical strategies for making feedback mechanisms visible and engaging to users, techniques for collecting segmented feedback that provides actionable insights, and methods for mining user behavior to generate training data. The chapter emphasizes how effective feedback collection transforms your RAG application from a static tool into a continuously improving system that grows more valuable with every interaction.
```

## Introduction

The true power of RAG isn't in its initial deployment—it's in how the system improves over time through feedback collection. Many RAG implementations focus exclusively on the technical details of retrieval and generation while neglecting the critical infrastructure needed to collect and utilize user feedback.

!!! note "Building on Previous Chapters" - **[Chapter 1](chapter1.md)**: The evaluation framework you built provides the baseline - **[Chapter 2](chapter2.md)**: The fine-tuning techniques need feedback data to be effective

    This chapter shows you how to collect the data that powers continuous improvement.

In this chapter, we'll explore how to build effective feedback mechanisms that transform your RAG application from a static implementation into a continuously improving system that grows more valuable with every user interaction. This approach creates a "feedback flywheel"—a virtuous cycle where user interactions provide the data needed to make the system better, which in turn attracts more users and generates more feedback.

!!! warning "The Invisible Feedback Problem"
Many RAG implementations hide feedback mechanisms in obscure UI locations or use generic "thumbs up/down" buttons that provide minimal insight. Research suggests that users interact with these minimal feedback options less than 0.1% of the time, providing insufficient data for meaningful improvements.

In my consulting practice, I've seen that simply changing the copy from generic "How did we do?" to specific "Did we answer your question?" can increase feedback rates by **5x**. Well-designed feedback mechanisms don't just collect more data—they accelerate your entire improvement cycle, allowing you to fine-tune 5x faster and deploy with greater confidence.

!!! success "Proven Copy That Works"
**5x Better Feedback Rates:** - ✅ "Did we answer your question?" - ✅ "Was this information helpful?" - ✅ "Did we take the correct actions?" (for action-oriented systems) - ❌ "How did we do?" - ❌ "Rate your experience"

    **Context-Specific Examples:**
    - For coding assistants: "Did this code solve your problem?"
    - For customer support: "Did we resolve your issue?"
    - For research tools: "Did you find what you were looking for?"
    - For data analysis: "Were these insights useful?"

    The key is focusing on the core value proposition rather than generic satisfaction.

Feedback collection is the lifeblood of systematic RAG improvement. Without it, you're flying blind—unable to identify which aspects of your system are performing well and which need enhancement. Robust feedback mechanisms tell you:

- Which queries your retrieval system handles poorly
- Which document segments are most valuable for answering specific questions
- Where your generation step produces inaccurate or unhelpful responses

This chapter focuses on the practical implementation of feedback mechanisms in RAG applications. We'll cover strategies for making feedback visible and engaging, approaches for segmenting feedback to make it more actionable, and techniques for mining user behavior to generate training datasets.

## Feedback Visibility: Make It Impossible to Miss

The first principle of effective feedback collection is visibility. Your feedback mechanisms should be prominent and engaging, not hidden in dropdown menus or settings pages. Users should encounter feedback options naturally as part of their interaction flow.

!!! example "High-Visibility Feedback UI"
Consider the difference between these two approaches:

```
**Low Visibility:** A small thumbs up/down icon in the corner of the response

**High Visibility:**

After receiving an answer, users see:

"Was this answer helpful? [Yes] [Somewhat] [No]"

If they click "Somewhat" or "No":

"What could be improved?"
- [ ] More detailed explanation
- [ ] More relevant information
- [ ] Incorrect information
- [ ] Better formatting
- [ ] Other: ____________
```

The second approach not only makes feedback impossible to miss but also structures it in a way that provides more actionable insights. Research shows that visible, engaging feedback mechanisms can increase feedback rates from less than 1% to over 30%.

### Implementation Strategies

Here are several patterns for implementing high-visibility feedback mechanisms:

1. **Inline Feedback:** Place feedback options directly beneath each response
1. **Modal Prompts:** Show a feedback modal after a certain number of interactions
1. **Follow-up Questions:** Include feedback collection as part of conversational flow
1. **Email Follow-ups:** Send follow-up emails asking for feedback on recent sessions

Each approach has advantages for different use cases. The key is to make feedback collection a natural part of the user experience rather than an afterthought.

!!! tip "Streaming and Perceived Performance"
**The Claude Progress Counter Effect:**

    Claude's implementation of progress counters during response generation serves multiple purposes:
    - Shows "thinking" progress (e.g., "Analyzing document 3 of 5...")
    - Reduces perceived latency by up to 45%
    - Gives users confidence the system is working
    - Creates natural moments for feedback collection

    **Implementation Pattern:**
    ```
    Searching documents... [████░░░░░░] 40%
    Found 5 relevant sources
    Analyzing content... [████████░░] 80%
    Generating response... [██████████] 100%

    [Response appears here]

    Did we find the right information? [Yes] [No]
    ```

    This pattern makes feedback feel like a natural continuation of the interaction rather than an interruption.

### Enterprise Feedback Collection with Slack Integration

For enterprise applications, especially when working with large customers who have dedicated customer success teams, consider implementing a Slack integration for feedback collection:

1. Create a shared Slack channel with customer stakeholders
1. Post negative feedback directly to the channel in real-time
1. Allow your team to discuss issues and ask follow-up questions
1. Document how feedback is addressed and integrated into your evaluation suite
1. Report back on improvements during regular sync meetings

This approach creates transparency and builds trust by showing customers that their feedback drives real improvements. In my experience, this method increases feedback by approximately 5x compared to traditional forms, while also improving customer retention through visible responsiveness.

!!! example "Enterprise Feedback Pattern"
**The Most Effective B2B Feedback Flow:**

    1. **In-App Collection:**
       - Binary feedback (thumbs up/down) for quick signals
       - Optional text field appears only after negative feedback
       - Track which employee provided feedback

    2. **Slack Integration:**
       ```
       🚨 Negative Feedback Alert
       User: sarah@company.com
       Query: "Find all contracts with termination clauses"
       Issue: Missing several key documents
       Response ID: #12345

       [View Full Context] [Reply to User]
       ```

    3. **Follow-Up:**
       - Customer success team can immediately engage
       - Engineering team sees issues in real-time
       - Creates accountability and trust

    This pattern has helped teams achieve 30-40% feedback rates in enterprise settings.

!!! example "Slack Webhook Integration Code"
![Example of Slack feedback integration showing code that posts negative feedback to a Slack channel](../assets/images/slack-feedback-code.png)

```
*This code demonstrates how to integrate feedback collection with Slack, automatically posting negative feedback to a shared channel for immediate visibility and follow-up.*
```

!!! example "Feedback UI Implementation"
![Example of feedback UI implementation showing a Python function that generates HTML with feedback buttons](../assets/images/feedback-ui-code.png)

```
*This code renders a response with prominent feedback options, automatically showing a more detailed form if the user indicates the response wasn't fully helpful.*
```

## Segmented Feedback: Make It Actionable

Generic feedback like thumbs up/down provides minimal insight for improvement. To make feedback truly actionable, segment it into specific aspects of your RAG pipeline.

!!! warning "The Problem with Generic Feedback"
A simple "thumbs down" could mean many things: - The retrieval system found irrelevant documents - The generation step produced inaccurate information - The answer was technically correct but poorly formatted - The answer was too brief or too verbose

```
Without knowing which aspect failed, you can't target improvements effectively.
```

Segmented feedback isolates specific parts of your RAG pipeline, helping you identify exactly where issues occur. Instead of asking "Was this helpful?" consider questions like:

- "Did this answer directly address your question?"
- "Was the information factually accurate?"
- "Were sources relevant to your query?"
- "Was the response clear and well-organized?"

Each question targets a different aspect of your system, allowing you to pinpoint areas for improvement.

### Collecting Segmented Negative Feedback

Negative feedback is particularly valuable for improvement, but users often abandon interactions after having a bad experience. To maximize the collection of negative feedback:

1. Make feedback collection immediate—don't wait until the end of a session
1. Use progressive disclosure to collect more detailed feedback after an initial negative response
1. Keep detailed feedback optional but make it easy to provide
1. Explain how feedback will be used to improve the system

Here's how you might implement segmented negative feedback collection:

## Learning from User Behavior: The Implicit Feedback Gold Mine

While explicit feedback (ratings, comments) is valuable, users express opinions through their actions even when they don't provide direct feedback. These behavioral signals—often called implicit feedback—can be a gold mine for system improvement.

Key implicit feedback signals include:

- **Query refinements:** When users rephrase a query immediately after receiving a response
- **Abandonment:** When users abandon a session after receiving a response
- **Engagement time:** How long users engage with a response
- **Link clicks:** Which citations or references users click on
- **Copypaste actions:** What parts of responses users copy to their clipboard
- **Scrolling behavior:** Whether users read the entire response or just skim

By tracking these behaviors, you can identify patterns that indicate success or failure even when users don't provide explicit feedback.

!!! example "Implicit Feedback Collection"
![Example of JavaScript code for tracking implicit feedback signals](../assets/images/implicit-feedback-code.png)

```
*This code tracks key implicit feedback signals including query refinements, citation clicks, and engagement time, providing valuable data even when users don't explicitly rate responses.*
```

### Mining Hard Negatives from User Behavior

One particularly valuable form of implicit feedback is the identification of "hard negatives"—documents that appear relevant based on keyword or semantic matching but are actually irrelevant or misleading for a particular query.

When a user submits a query, views the response and citations, then immediately refines their query or provides negative feedback, there's a good chance that the retrieved documents were not helpful. These interactions provide strong signals about weaknesses in your retrieval system.

By tracking these patterns, you can build datasets of queries paired with documents that should NOT be retrieved—invaluable training data for improving embedding models or reranking systems.

#### Creative UI Patterns for Hard Negative Collection

Consider these UI patterns specifically designed to help collect hard negative examples:

1. **Interactive Citations**: Display the source documents used to generate the response and allow users to mark specific citations as irrelevant. This direct feedback creates perfect triplets for contrastive learning (query → relevant docs → irrelevant docs).

1. **Document Filtering UI**: Similar to how social networks show "People You May Know," present a scrollable list of potentially relevant documents and let users remove irrelevant ones. Each removal creates a hard negative training example.

1. **Limited Options with Refresh**: Show only the top 5 most relevant documents, with options to "add" (positive) or "delete" (negative) each one. When a user deletes a document to see another option, you've collected a hard negative.

1. **Regeneration After Removal**: Allow users to remove citation sources and then regenerate the answer. Documents removed before regeneration become strong hard negative candidates for that query.

!!! example "Interactive Citations UI"
![Example of interactive citations UI with buttons to mark sources as relevant or irrelevant](../assets/images/interactive-citations-ui.png)

```
*This UI allows users to mark specific citations as relevant or irrelevant and regenerate answers, creating valuable training data for improving retrieval quality.*

Remember: Hard negatives are the most valuable training examples for improving retrieval quality through embedding model fine-tuning. While standard negatives (completely unrelated documents) are easy to find, hard negatives (seemingly relevant but actually unhelpful documents) are rare and therefore extremely valuable for training.
```

Here's a simple algorithm for mining hard negatives from user interactions:

By collecting these potential hard negatives over time, you can build a dataset for fine-tuning embedding models or training re-rankers to avoid these problematic documents in future queries.

## Citations for Building Trust and Collecting Feedback

Citations are a powerful tool that serves multiple purposes in a RAG system:

1. **Building trust**: Users want to know where information comes from and how the AI found it
1. **Providing transparency**: Citations show what data is being used to generate responses
1. **Collecting feedback**: Citations create opportunities to gather document-level relevance signals

When users can see and interact with the source documents used in responses, they gain confidence in the system and are more likely to provide feedback on the quality and relevance of these sources.

### Implementing Interactive Citations

There are several approaches to implementing citations in your RAG interface:

1. **Markdown links**: A simple implementation using markdown formatting to link to source documents
1. **Numbered citations**: Academic-style numbered references with hover previews
1. **Inline highlights**: Highlighting portions of text with the source documents they came from
1. **Visual PDF overlays**: For document-based applications, highlighting the exact location in a PDF

!!! example "Markdown-based Citation Implementation"
![Example of JavaScript code for implementing markdown-based citations with feedback options](../assets/images/citations-implementation.png)

```
*This code formats responses with clickable citations and builds a reference list that includes feedback options for each source, helping collect document-level relevance signals.*
```

### Advanced Visualization with Bounding Boxes

For document-centric applications, consider implementing bounding box citations that highlight the exact location in the source documents:

1. Store coordinates of key information in your vector database
1. When generating responses, include these coordinates in citation metadata
1. Render the original document with visual overlays on the cited portions
1. Allow users to click citations in the answer to jump to the exact location in the document

This approach is particularly valuable for PDF-heavy domains like legal, medical, or technical documentation where source verification is critical.

### Citation Implementation Patterns

!!! quote "Preventing Hallucinations"
Skylar Payne emphasizes that hallucination remains a critical challenge, especially in sensitive domains. His most effective approach: "Force the LLM to provide inline citations, validate that each citation exists in the retrieved documents, and semantically validate that each citation actually supports the claimed content."

    This is particularly critical for healthcare, legal, and financial applications. [See more anti-patterns to avoid →](../talks/rag-antipatterns-skylar-payne.md)

!!! info "XML-Based Citation Pattern"
**The Most Robust Approach:**

    Instead of relying on markdown links or footnotes, use XML tags with start/end word anchoring:

    ```xml
    According to the contract, <cite source="doc123" start="450" end="467">the termination
    clause requires 30 days notice</cite> and <cite source="doc124" start="122" end="134">
    includes a penalty fee of $10,000</cite>.
    ```

    **Benefits:**
    - Survives markdown parsing
    - Enables precise highlighting
    - Works well with fine-tuning
    - Handles abbreviations and technical language

    **Fine-Tuning for Citations:**
    - Train models to generate these XML tags
    - Use your evaluation data as training examples
    - Particularly effective for domains with heavy abbreviations (medical, legal, technical)

## Building a Feedback-Driven Roadmap

The ultimate goal of feedback collection is to guide your improvement roadmap. Rather than making enhancement decisions based on intuition or technical interest, you can prioritize based on user needs revealed through feedback.

!!! info "Production Monitoring: Beyond Basic Feedback"
Ben Hylak and Sidhant Bendre highlight a critical insight: "There's no exception being thrown when something goes wrong - the model simply produces an inadequate response." Their approach combines implicit signals (user frustration, task failures) with explicit signals (ratings, regenerations) to identify issues that traditional monitoring misses. The Trellis framework they present helps organize the "infinite chaos" of AI outputs into controllable segments. [Learn about production monitoring strategies →](../talks/online-evals-production-monitoring-ben-sidhant.md)

A feedback-driven roadmap:

1. Identifies the most common issues reported by users
1. Quantifies the impact of each issue on user satisfaction
1. Ranks potential improvements by expected impact
1. Establishes clear metrics to evaluate whether changes actually improve the user experience

This approach ensures that engineering efforts focus on changes that will have the greatest impact on user satisfaction rather than on the most technically interesting problems.

## Conclusion: Feedback as Foundation

Effective feedback collection is the foundation of systematic RAG improvement. Without robust feedback mechanisms, you're left guessing about which aspects of your system need enhancement and whether your changes actually improve the user experience.

By implementing the strategies outlined in this chapter—making feedback visible, segmenting it for actionability, mining user behaviors for implicit signals, and using feedback to drive your roadmap—you establish a data-driven approach to continuous improvement.

The investment in well-designed feedback mechanisms pays extraordinary dividends:

1. **Accelerated improvement cycles**: With 5x more feedback, you can fine-tune models 5x faster
1. **Higher-quality training data**: Hard negatives mined from user interactions dramatically improve retrieval quality
1. **Increased user trust**: Citations and transparency build confidence in your system's outputs
1. **Better prioritization**: Clear signals about which issues matter most to users
1. **Data-driven roadmap**: Engineering priorities driven by user needs, not technical curiosity

Remember that small UX changes can make enormous differences in feedback collection rates. The most successful RAG applications aren't always those with the most sophisticated technology—they're the ones that most effectively learn from their users.

In the next chapter, we'll explore how to reduce perceived latency through streaming and progressive responses, building on the feedback foundation to create a more engaging user experience.

!!! info "How This Chapter Connects Forward" - **[Chapter 4](chapter4-2.md)**: The feedback you collect enables query segmentation and analysis - **[Chapter 5](chapter5-1.md)**: User behavior patterns reveal which specialized retrievers to build - **[Chapter 6](chapter6-2.md)**: Feedback on router decisions improves tool selection

## Reflection Questions

1. How visible are the feedback mechanisms in your current RAG implementation? What changes could make them more prominent and engaging?

1. What implicit signals could you collect from user interactions with your system? How might these complement explicit feedback?

1. How could you segment feedback to better pinpoint issues in specific parts of your RAG pipeline?

1. What processes would you need to implement to translate feedback into a prioritized improvement roadmap?

1. How might you incentivize users to provide more detailed feedback, especially after negative experiences?

## Summary

Effective feedback collection is essential for systematic improvement of RAG systems. By making feedback mechanisms visible and engaging, segmenting feedback to target specific pipeline components, mining implicit signals from user behavior, and using feedback to drive your improvement roadmap, you create a foundation for continuous enhancement. The feedback flywheel turns raw user interactions into actionable insights that guide your development priorities and measure the impact of your improvements.

### Key Takeaways

1. **Feedback Copy Matters**: Changing from generic "How did we do?" to specific "Did we answer your question?" can increase feedback rates by 5x.

1. **Enterprise Patterns**: For B2B applications, Slack integrations that post feedback directly to shared channels create transparency and trust while dramatically increasing feedback rates.

1. **Hard Negative Mining**: Design your UX to collect hard negatives—documents that appear relevant but are actually unhelpful—as they're the most valuable training examples for fine-tuning.

1. **Citation Benefits**: Interactive citations serve multiple purposes: building trust, providing transparency, and creating opportunities to collect document-level relevance signals.

1. **Behavior Tracking**: Implicit signals from user behavior (query refinements, dwell time, citation clicks) can provide even more training data than explicit feedback.

1. **Start Small**: Begin with simple, high-visibility feedback mechanisms and gradually add sophistication as you learn what works for your specific users and use cases.

!!! success "Quick Implementation Wins"
**Start with these proven patterns:**

    1. **Change your feedback copy** to "Did we answer your question?" (immediate 5x improvement)
    2. **Add streaming progress indicators** to reduce perceived latency by 45%
    3. **Implement XML-based citations** for robust source tracking
    4. **Set up Slack webhooks** for enterprise customers
    5. **Track query refinements** as implicit negative signals

    These changes can typically be implemented in 1-2 sprints and deliver immediate, measurable improvements.

## Additional Resources

1. Nielsen Norman Group, ["User Feedback Mechanisms for Mobile and Web"](https://www.nngroup.com/articles/feedback-mechanisms/)

1. Google Research, ["Beyond A/B Testing: Implicit Feedback for UI Improvement"](https://research.google/pubs/beyond-a-b-testing-implicit-feedback-for-ui-improvement/)

1. Qualtrics, ["Designing Feedback Forms That Users Actually Complete"](https://www.qualtrics.com/experience-management/customer/feedback-form-design/)

1. GitHub Repository: [RAG-Feedback-Collection](https://github.com/microsoft/rag-feedback-collection) - Templates and examples for implementing feedback mechanisms in RAG applications

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
