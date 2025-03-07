---
title: "Chapter 3.1: Feedback Collection"
description: "Building feedback flywheels into your RAG applications"
author: "Jason Liu"
---

!!! abstract "Chapter Overview"
This chapter explores the essential role of feedback collection in RAG systems, introducing the concept of a feedback flywheel for systematic improvement. You'll learn practical strategies for making feedback mechanisms visible and engaging to users, techniques for collecting segmented feedback that provides actionable insights, and methods for mining user behavior to generate training data. The chapter emphasizes how effective feedback collection transforms your RAG application from a static tool into a continuously improving system that grows more valuable with every interaction.

# Feedback Collection: Building Your Improvement Flywheel

## Introduction

The true power of RAG isn't in its initial deployment—it's in how the system improves over time through feedback collection. Many RAG implementations focus exclusively on the technical details of retrieval and generation while neglecting the critical infrastructure needed to collect and utilize user feedback.

In this chapter, we'll explore how to build effective feedback mechanisms that transform your RAG application from a static implementation into a continuously improving system that grows more valuable with every user interaction. This approach creates a "feedback flywheel"—a virtuous cycle where user interactions provide the data needed to make the system better, which in turn attracts more users and generates more feedback.

!!! warning "The Invisible Feedback Problem"
Many RAG implementations hide feedback mechanisms in obscure UI locations or use generic "thumbs up/down" buttons that provide minimal insight. Research suggests that users interact with these minimal feedback options less than 0.1% of the time, providing insufficient data for meaningful improvements.

Feedback collection is the lifeblood of systematic RAG improvement. Without it, you're flying blind—unable to identify which aspects of your system are performing well and which need enhancement. Robust feedback mechanisms tell you:

- Which queries your retrieval system handles poorly
- Which document segments are most valuable for answering specific questions
- Where your generation step produces inaccurate or unhelpful responses

This chapter focuses on the practical implementation of feedback mechanisms in RAG applications. We'll cover strategies for making feedback visible and engaging, approaches for segmenting feedback to make it more actionable, and techniques for mining user behavior to generate training datasets.

## Feedback Visibility: Make It Impossible to Miss

The first principle of effective feedback collection is visibility. Your feedback mechanisms should be prominent and engaging, not hidden in dropdown menus or settings pages. Users should encounter feedback options naturally as part of their interaction flow.

!!! example "High-Visibility Feedback UI"
Consider the difference between these two approaches:

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

The second approach not only makes feedback impossible to miss but also structures it in a way that provides more actionable insights. Research shows that visible, engaging feedback mechanisms can increase feedback rates from less than 1% to over 30%.

### Implementation Strategies

Here are several patterns for implementing high-visibility feedback mechanisms:

1. **Inline Feedback:** Place feedback options directly beneath each response
2. **Modal Prompts:** Show a feedback modal after a certain number of interactions
3. **Follow-up Questions:** Include feedback collection as part of conversational flow
4. **Email Follow-ups:** Send follow-up emails asking for feedback on recent sessions

Each approach has advantages for different use cases. The key is to make feedback collection a natural part of the user experience rather than an afterthought.

```python
def render_response_with_feedback(response: str, query_id: str):
    """
    Render a response with prominent feedback mechanisms.

    Parameters:
    - response: The generated response text
    - query_id: Unique identifier for the query

    Returns:
    - HTML content with embedded feedback UI
    """
    html = f"""
    <div class="response-container">
        <div class="response-content">
            {response}
        </div>

        <div class="feedback-container">
            <p class="feedback-prompt">Was this response helpful?</p>

            <div class="feedback-options">
                <button onclick="recordFeedback('{query_id}', 'helpful')">
                    Very helpful
                </button>

                <button onclick="recordFeedback('{query_id}', 'somewhat')">
                    Somewhat helpful
                </button>

                <button onclick="recordFeedback('{query_id}', 'not_helpful')">
                    Not helpful
                </button>
            </div>
        </div>
    </div>

    <script>
    function recordFeedback(id, rating) {
        // Record the initial feedback
        fetch('/api/feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query_id: id,
                rating: rating
            })
        })
        .then(response => response.json())
        .then(data => {
            // If the rating wasn't "very helpful", show the detailed feedback form
            if (rating !== 'helpful') {
                showDetailedFeedbackForm(id, rating);
            } else {
                showThankYouMessage();
            }
        });
    }

    function showDetailedFeedbackForm(id, initialRating) {
        // Display a more detailed feedback form based on the initial rating
        // ...
    }
    </script>
    """

    return html
```

## Segmented Feedback: Make It Actionable

Generic feedback like thumbs up/down provides minimal insight for improvement. To make feedback truly actionable, segment it into specific aspects of your RAG pipeline.

!!! warning "The Problem with Generic Feedback"
A simple "thumbs down" could mean many things: - The retrieval system found irrelevant documents - The generation step produced inaccurate information - The answer was technically correct but poorly formatted - The answer was too brief or too verbose

    Without knowing which aspect failed, you can't target improvements effectively.

Segmented feedback isolates specific parts of your RAG pipeline, helping you identify exactly where issues occur. Instead of asking "Was this helpful?" consider questions like:

- "Did this answer directly address your question?"
- "Was the information factually accurate?"
- "Were sources relevant to your query?"
- "Was the response clear and well-organized?"

Each question targets a different aspect of your system, allowing you to pinpoint areas for improvement.

### Collecting Segmented Negative Feedback

Negative feedback is particularly valuable for improvement, but users often abandon interactions after having a bad experience. To maximize the collection of negative feedback:

1. Make feedback collection immediate—don't wait until the end of a session
2. Use progressive disclosure to collect more detailed feedback after an initial negative response
3. Keep detailed feedback optional but make it easy to provide
4. Explain how feedback will be used to improve the system

Here's how you might implement segmented negative feedback collection:

```python
def collect_negative_feedback(query_id: str, response_id: str):
    """
    Generate a detailed negative feedback form.

    Parameters:
    - query_id: ID of the original query
    - response_id: ID of the response being rated

    Returns:
    - HTML for a segmented feedback form
    """
    return f"""
    <div class="detailed-feedback-form">
        <p>Thanks for your feedback. Could you tell us more about what wasn't helpful?</p>

        <form id="detailed-feedback-{response_id}">
            <input type="hidden" name="query_id" value="{query_id}">
            <input type="hidden" name="response_id" value="{response_id}">

            <h4>What issues did you notice? (Select all that apply)</h4>

            <div class="feedback-section">
                <h5>Retrieval Issues:</h5>
                <label>
                    <input type="checkbox" name="retrieval_issue" value="irrelevant_sources">
                    Sources weren't relevant to my question
                </label>
                <label>
                    <input type="checkbox" name="retrieval_issue" value="missing_information">
                    Important information seemed to be missing
                </label>
            </div>

            <div class="feedback-section">
                <h5>Generation Issues:</h5>
                <label>
                    <input type="checkbox" name="generation_issue" value="inaccurate">
                    Information was factually incorrect
                </label>
                <label>
                    <input type="checkbox" name="generation_issue" value="formatting">
                    Response was poorly organized or formatted
                </label>
                <label>
                    <input type="checkbox" name="generation_issue" value="incomplete">
                    Answer was incomplete or too brief
                </label>
            </div>

            <div class="feedback-section">
                <h5>Additional Comments:</h5>
                <textarea name="comments" placeholder="Any other feedback to help us improve?"></textarea>
            </div>

            <button type="submit">Submit Feedback</button>
        </form>
    </div>

    <script>
    document.getElementById("detailed-feedback-{response_id}").addEventListener("submit", function(e) {
        e.preventDefault();

        // Collect form data
        const formData = new FormData(e.target);
        const feedbackData = {
            query_id: formData.get("query_id"),
            response_id: formData.get("response_id"),
            retrieval_issues: formData.getAll("retrieval_issue"),
            generation_issues: formData.getAll("generation_issue"),
            comments: formData.get("comments")
        };

        // Submit detailed feedback
        fetch('/api/detailed-feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(feedbackData)
        })
        .then(response => response.json())
        .then(data => {
            showThankYouMessage();
        });
    });
    </script>
    """
```

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

    ```javascript
    // Track query refinements
    function trackQueryRefinement(originalQueryId, newQuery) {
      fetch('/api/track-refinement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          original_query_id: originalQueryId,
          new_query: newQuery,
          time_difference_ms: Date.now() - lastQueryTimestamp
        })
      });
    }

    // Track citation clicks
    function trackCitationClick(queryId, responseId, citationIndex, documentId) {
      fetch('/api/track-citation-click', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query_id: queryId,
          response_id: responseId,
          citation_index: citationIndex,
          document_id: documentId,
          timestamp: Date.now()
        })
      });
    }

    // Track user engagement time
    let viewStartTime = Date.now();
    let isVisible = true;

    document.addEventListener('visibilitychange', function() {
      if (document.visibilityState === 'hidden') {
        isVisible = false;
        trackEngagementTime();
      } else {
        isVisible = true;
        viewStartTime = Date.now();
      }
    });

    window.addEventListener('beforeunload', function() {
      trackEngagementTime();
    });

    function trackEngagementTime() {
      if (!isVisible) return;

      const engagementTimeMs = Date.now() - viewStartTime;

      fetch('/api/track-engagement', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query_id: currentQueryId,
          response_id: currentResponseId,
          engagement_time_ms: engagementTimeMs
        })
      });
    }
    ```

### Mining Hard Negatives from User Behavior

One particularly valuable form of implicit feedback is the identification of "hard negatives"—documents that appear relevant based on keyword or semantic matching but are actually irrelevant or misleading for a particular query.

When a user submits a query, views the response and citations, then immediately refines their query or provides negative feedback, there's a good chance that the retrieved documents were not helpful. These interactions provide strong signals about weaknesses in your retrieval system.

By tracking these patterns, you can build datasets of queries paired with documents that should NOT be retrieved—invaluable training data for improving embedding models or reranking systems.

Here's a simple algorithm for mining hard negatives from user interactions:

```python
def identify_potential_hard_negatives(
    query_id: str,
    retrieved_docs: List[str],
    user_actions: List[Dict]
) -> List[Dict]:
    """
    Identify potential hard negative documents based on user interactions.

    Parameters:
    - query_id: The ID of the original query
    - retrieved_docs: List of document IDs retrieved for this query
    - user_actions: Sequence of user actions following the response

    Returns:
    - List of potential hard negative documents with confidence scores
    """
    hard_negative_candidates = []

    # Check for immediate query refinement (within 30 seconds)
    refinement = next(
        (
            action for action in user_actions
            if action["type"] == "query" and action["timestamp"] - query_timestamp < 30
        ),
        None
    )

    if refinement:
        # All retrieved docs from the original query are potential hard negatives
        # But we assign different confidence scores based on user actions
        for doc_id in retrieved_docs:
            confidence = 0.7  # Base confidence for refinement case

            # Check if user viewed this document (reduces confidence it's a hard negative)
            if any(a["type"] == "view_document" and a["document_id"] == doc_id for a in user_actions):
                confidence -= 0.3

            # Check if user explicitly marked this document as irrelevant
            if any(a["type"] == "rate_document" and a["document_id"] == doc_id and a["rating"] == "irrelevant" for a in user_actions):
                confidence = 0.9  # Very high confidence it's a hard negative

            hard_negative_candidates.append({
                "query_id": query_id,
                "document_id": doc_id,
                "confidence": confidence,
                "reason": "query_refinement"
            })

    # Check for negative feedback on response
    negative_feedback = next(
        (
            action for action in user_actions
            if action["type"] == "rate_response" and action["rating"] in ["not_helpful", "inaccurate"]
        ),
        None
    )

    if negative_feedback:
        # Documents that weren't explicitly marked as helpful may be hard negatives
        for doc_id in retrieved_docs:
            # Skip documents the user explicitly marked as helpful
            if any(a["type"] == "rate_document" and a["document_id"] == doc_id and a["rating"] == "helpful" for a in user_actions):
                continue

            confidence = 0.5  # Base confidence for negative feedback case

            # Adjust confidence based on document interactions
            if any(a["type"] == "rate_document" and a["document_id"] == doc_id and a["rating"] == "irrelevant" for a in user_actions):
                confidence = 0.9  # Very high confidence it's a hard negative

            hard_negative_candidates.append({
                "query_id": query_id,
                "document_id": doc_id,
                "confidence": confidence,
                "reason": "negative_feedback"
            })

    # Filter out low-confidence candidates
    return [candidate for candidate in hard_negative_candidates if candidate["confidence"] > 0.4]
```

By collecting these potential hard negatives over time, you can build a dataset for fine-tuning embedding models or training re-rankers to avoid these problematic documents in future queries.

## Building a Feedback-Driven Roadmap

The ultimate goal of feedback collection is to guide your improvement roadmap. Rather than making enhancement decisions based on intuition or technical interest, you can prioritize based on user needs revealed through feedback.

A feedback-driven roadmap:

1. Identifies the most common issues reported by users
2. Quantifies the impact of each issue on user satisfaction
3. Ranks potential improvements by expected impact
4. Establishes clear metrics to evaluate whether changes actually improve the user experience

This approach ensures that engineering efforts focus on changes that will have the greatest impact on user satisfaction rather than on the most technically interesting problems.

```python
def analyze_feedback_for_roadmap(feedback_data: List[Dict], time_period_days: int = 30):
    """
    Analyze feedback data to identify high-priority improvement areas.

    Parameters:
    - feedback_data: Collection of user feedback and interaction data
    - time_period_days: Time window to analyze (default: 30 days)

    Returns:
    - Dictionary of issue categories with frequency and impact scores
    """
    recent_cutoff = datetime.now() - timedelta(days=time_period_days)
    recent_feedback = [f for f in feedback_data if f["timestamp"] > recent_cutoff]

    # Group feedback by issue category
    issues_by_category = defaultdict(list)

    for feedback in recent_feedback:
        if "issues" in feedback:
            for issue in feedback["issues"]:
                category = issue["category"]
                issues_by_category[category].append({
                    "feedback_id": feedback["id"],
                    "severity": issue.get("severity", "medium"),
                    "user_id": feedback.get("user_id", "anonymous"),
                    "timestamp": feedback["timestamp"]
                })

    # Calculate impact scores
    impact_scores = {}

    for category, issues in issues_by_category.items():
        # Count unique users affected
        unique_users = len(set(issue["user_id"] for issue in issues if issue["user_id"] != "anonymous"))

        # Calculate frequency
        frequency = len(issues) / len(recent_feedback)

        # Calculate severity score (0-1)
        severity_map = {"low": 0.3, "medium": 0.6, "high": 1.0}
        avg_severity = sum(severity_map[issue["severity"]] for issue in issues) / len(issues)

        # Calculate recency factor (more recent issues weighted higher)
        most_recent = max(issue["timestamp"] for issue in issues)
        recency_factor = 1.0 - ((datetime.now() - most_recent).days / time_period_days)

        # Calculate overall impact score
        impact = (frequency * 0.4) + (avg_severity * 0.3) + (unique_users / 100 * 0.2) + (recency_factor * 0.1)

        impact_scores[category] = {
            "frequency": frequency,
            "unique_users": unique_users,
            "avg_severity": avg_severity,
            "recency_factor": recency_factor,
            "overall_impact": impact,
            "example_feedbacks": [issue["feedback_id"] for issue in issues[:5]]
        }

    # Sort by impact score
    sorted_impact = sorted(
        impact_scores.items(),
        key=lambda x: x[1]["overall_impact"],
        reverse=True
    )

    return {
        "analyzed_period_days": time_period_days,
        "total_feedback_count": len(recent_feedback),
        "prioritized_issues": sorted_impact
    }
```

## Conclusion: Feedback as Foundation

Effective feedback collection is the foundation of systematic RAG improvement. Without robust feedback mechanisms, you're left guessing about which aspects of your system need enhancement and whether your changes actually improve the user experience.

By implementing the strategies outlined in this chapter—making feedback visible, segmenting it for actionability, mining user behaviors for implicit signals, and using feedback to drive your roadmap—you establish a data-driven approach to continuous improvement.

In the next chapter, we'll explore how to reduce perceived latency through streaming and progressive responses, building on the feedback foundation to create a more engaging user experience.

## Reflection Questions

1. How visible are the feedback mechanisms in your current RAG implementation? What changes could make them more prominent and engaging?

2. What implicit signals could you collect from user interactions with your system? How might these complement explicit feedback?

3. How could you segment feedback to better pinpoint issues in specific parts of your RAG pipeline?

4. What processes would you need to implement to translate feedback into a prioritized improvement roadmap?

5. How might you incentivize users to provide more detailed feedback, especially after negative experiences?

## Summary

Effective feedback collection is essential for systematic improvement of RAG systems. By making feedback mechanisms visible and engaging, segmenting feedback to target specific pipeline components, mining implicit signals from user behavior, and using feedback to drive your improvement roadmap, you create a foundation for continuous enhancement. The feedback flywheel turns raw user interactions into actionable insights that guide your development priorities and measure the impact of your improvements.

## Additional Resources

1. Nielsen Norman Group, ["User Feedback Mechanisms for Mobile and Web"](https://www.nngroup.com/articles/feedback-mechanisms/)

2. Google Research, ["Beyond A/B Testing: Implicit Feedback for UI Improvement"](https://research.google/pubs/beyond-a-b-testing-implicit-feedback-for-ui-improvement/)

3. Qualtrics, ["Designing Feedback Forms That Users Actually Complete"](https://www.qualtrics.com/experience-management/customer/feedback-form-design/)

4. GitHub Repository: [RAG-Feedback-Collection](https://github.com/microsoft/rag-feedback-collection) - Templates and examples for implementing feedback mechanisms in RAG applications
