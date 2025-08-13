# Better Summaries: Building Domain-Specific Clustering

> **Series Overview**: This is the second notebook in our three-part series on systematically analyzing and improving RAG systems. In the first notebook, we discovered query patterns but found limitations with generic summaries. Now we'll fix that.

> **Prerequisites**: Complete "1. Cluster Conversations" notebook first. You'll need the same dependencies and `GOOGLE_API_KEY` from the previous notebook.

## Why This Matters

**The generic summaries from our initial clustering missed crucial details that would enable effective query understanding.** When working with specialized domains like machine learning experiment tracking, generic descriptions like "user seeks information about tracking" fail to capture the specific W&B features, user goals, and pain points that matter for system improvement.

**Custom summarization transforms vague descriptions into precise, actionable insights.** Instead of "user requests assistance with tool integration," we can generate "user is configuring W&B Artifacts for model versioning in PyTorch workflows." This precision is critical for building clusters that truly reflect how users interact with your platform.

Domain-specific summaries enable us to:

1. **Capture exact features** users are working with (Artifacts, Configs, Reports)
2. **Identify specific goals** and pain points rather than generic categories
3. **Reveal usage patterns** that generic summaries obscure
4. **Create foundations** for more targeted system improvements

## What You'll Learn

In this notebook, you'll discover how to:

1. **Build Custom Summary Models**

   - Design specialized prompts that extract domain-specific information
   - Implement length constraints for focused, consistent summaries
   - Replace Kura's default summarization with your custom approach

2. **Compare Summarization Approaches**

   - Analyze the limitations of generic vs. domain-specific summaries
   - See how improved summaries change clustering outcomes
   - Understand the impact of summary quality on cluster interpretability

3. **Generate Enhanced Clusters**
   - Apply custom summaries to create more representative topic groups
   - Configure clustering parameters for optimal domain-specific results
   - Extract actionable insights about user behavior patterns

## What You'll Discover

**By the end of this notebook, you'll transform your seven generic clusters into three highly actionable categories**: Access Controls (data export/security), Deployment (service integration/auth), and Experiment Management (artifacts/visualization/multi-GPU). This dramatic improvement in cluster quality—from vague topics to specific, actionable user needs—will provide the foundation for building production classifiers in the next notebook.

## The Power of Domain-Specific Clustering

**While generic clustering tells you "what" users are asking about, domain-specific clustering reveals "why" and "how" they're struggling.** This shift from surface-level topics to deep user intent understanding is what enables you to build targeted solutions rather than generic improvements.

By the end of this series, you'll have a complete framework for turning raw user queries into systematic, data-driven RAG improvements that address real user needs rather than perceived ones.

## Creating a Custom Summary Model

To address the limitations we identified in our default summaries, we'll now implement our own custom summary model specific to Weights & Biases queries. By replacing the generic summarization approach with a domain-tailored solution, we can generate summaries that precisely capture the tools, features, and goals relevant to W&B users.

The `WnBSummaryModel` class we'll create extends Kura's base `SummaryModel` with a specialized prompt that instructs the model to:

1. Identify specific W&B features mentioned in the query (e.g., Artifacts, Configs, Reports)
2. Clearly state the problem the user is trying to solve
3. Format responses concisely (25 words or less) to ensure summaries remain focused

This approach generates summaries that are not only more informative but also more consistent, making them ideal building blocks for meaningful clustering. Let's implement our custom model and see how it transforms our understanding of user query patterns.

### Loading in Conversation

Let's first start by loading in our conversations and parsing it into a list of `Conversation` objects that `Kura` can work with

```python
from kura import CheckpointManager, Conversation

checkpoint_manager = CheckpointManager("./checkpoints", enabled=True)
conversations = checkpoint_manager.load_checkpoint("conversations.jsonl", Conversation)
```

Let's now try to see how our default summaries look like

```python
from kura.summarisation import SummaryModel
from rich import print as rprint

summaries = await SummaryModel().summarise(conversations[:2])
for summary in summaries:
    rprint(summary)

```

    Summarising 2 conversations: 100%|██████████| 2/2 [00:02<00:00,  1.03s/it]

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">ConversationSummary</span><span style="font-weight: bold">(</span>
    <span style="color: #808000; text-decoration-color: #808000">summary</span>=<span style="color: #008000; text-decoration-color: #008000">'The user is seeking information on how to track machine learning experiments using a specific tool, </span>
<span style="color: #008000; text-decoration-color: #008000">including code examples and steps involved.'</span>,
    <span style="color: #808000; text-decoration-color: #808000">request</span>=<span style="color: #008000; text-decoration-color: #008000">"The user's overall request for the assistant is to provide guidance on experiment tracking in machine </span>
<span style="color: #008000; text-decoration-color: #008000">learning."</span>,
    <span style="color: #808000; text-decoration-color: #808000">topic</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">languages</span>=<span style="font-weight: bold">[</span><span style="color: #008000; text-decoration-color: #008000">'english'</span>, <span style="color: #008000; text-decoration-color: #008000">'python'</span><span style="font-weight: bold">]</span>,
    <span style="color: #808000; text-decoration-color: #808000">task</span>=<span style="color: #008000; text-decoration-color: #008000">'The task is to explain how to track machine learning experiments with code examples.'</span>,
    <span style="color: #808000; text-decoration-color: #808000">concerning_score</span>=<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>,
    <span style="color: #808000; text-decoration-color: #808000">user_frustration</span>=<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>,
    <span style="color: #808000; text-decoration-color: #808000">assistant_errors</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">chat_id</span>=<span style="color: #008000; text-decoration-color: #008000">'5e878c76-25c1-4bad-8cae-6a40ca4c8138'</span>,
    <span style="color: #808000; text-decoration-color: #808000">metadata</span>=<span style="font-weight: bold">{</span><span style="color: #008000; text-decoration-color: #008000">'conversation_turns'</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>, <span style="color: #008000; text-decoration-color: #008000">'query_id'</span>: <span style="color: #008000; text-decoration-color: #008000">'5e878c76-25c1-4bad-8cae-6a40ca4c8138'</span><span style="font-weight: bold">}</span>,
    <span style="color: #808000; text-decoration-color: #808000">embedding</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>
<span style="font-weight: bold">)</span>
</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">ConversationSummary</span><span style="font-weight: bold">(</span>
    <span style="color: #808000; text-decoration-color: #808000">summary</span>=<span style="color: #008000; text-decoration-color: #008000">'Bayesian optimization is a hyperparameter tuning technique that uses a surrogate function for informed</span>
<span style="color: #008000; text-decoration-color: #008000">search, contrasting with grid and random search methods.'</span>,
    <span style="color: #808000; text-decoration-color: #808000">request</span>=<span style="color: #008000; text-decoration-color: #008000">"The user's overall request for the assistant is to explain Bayesian optimization and its </span>
<span style="color: #008000; text-decoration-color: #008000">implementation for hyperparameter tuning."</span>,
    <span style="color: #808000; text-decoration-color: #808000">topic</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">languages</span>=<span style="font-weight: bold">[</span><span style="color: #008000; text-decoration-color: #008000">'english'</span>, <span style="color: #008000; text-decoration-color: #008000">'python'</span><span style="font-weight: bold">]</span>,
    <span style="color: #808000; text-decoration-color: #808000">task</span>=<span style="color: #008000; text-decoration-color: #008000">'The task is to provide information on Bayesian optimization and its application in hyperparameter </span>
<span style="color: #008000; text-decoration-color: #008000">tuning.'</span>,
    <span style="color: #808000; text-decoration-color: #808000">concerning_score</span>=<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>,
    <span style="color: #808000; text-decoration-color: #808000">user_frustration</span>=<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>,
    <span style="color: #808000; text-decoration-color: #808000">assistant_errors</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">chat_id</span>=<span style="color: #008000; text-decoration-color: #008000">'d7b77e8a-e86c-4953-bc9f-672618cdb751'</span>,
    <span style="color: #808000; text-decoration-color: #808000">metadata</span>=<span style="font-weight: bold">{</span><span style="color: #008000; text-decoration-color: #008000">'conversation_turns'</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>, <span style="color: #008000; text-decoration-color: #008000">'query_id'</span>: <span style="color: #008000; text-decoration-color: #008000">'d7b77e8a-e86c-4953-bc9f-672618cdb751'</span><span style="font-weight: bold">}</span>,
    <span style="color: #808000; text-decoration-color: #808000">embedding</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>
<span style="font-weight: bold">)</span>
</pre>

Looking at these default summaries, we can identify several key limitations that prevent them from being truly useful for clustering W&B-specific queries:

**Problems with Default Summaries**

1. Lack of Specificity: The first summary refers to "a specific tool" rather than explicitly naming Weights & Biases, missing the opportunity to highlight the domain context.

2. Missing Feature Details: Neither summary identifies which specific W&B features the users are interested in (experiment tracking, Bayesian optimization for hyperparameter tuning), which would be crucial for meaningful clustering.

These generic summaries would lead to clusters based primarily on query structure ("users asking for information") rather than meaningful W&B feature categories or user goals.

By defining our own summarisation model, we can address these limitations and cluster our user queries based off the specific problems and features they are trying to use.

### Defining Our New Summary Model

Let's now define a new `WnBSummaryModel` which will help address the shortcomings of the default summarisation model.

We'll do so by modifying the `summarise_conversation` method so that our summaries can become more precise and feature-focused. This allows us to better reflect how users interact with Weights and Biases and in turn translate to more representative clusters

```python
from kura.types import Conversation, ConversationSummary
from kura.summarisation import SummaryModel, GeneratedSummary
import instructor


class WnBSummaryModel(SummaryModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def summarise_conversation(
        self, conversation: Conversation
    ) -> ConversationSummary:

        client = instructor.from_provider("openai/gpt-4o-mini", async_client=True)
        async with self.semaphore:
            resp = await client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {
                        "role": "user",
                        "content": """
Analyze the user's query and the retrieved Weights and Biases documentation to provide a focused summary.

In your response:

1. Identify the specific W&B features being used, such as:
   - Experiment tracking and logging
   - Hyperparameter optimization
   - Model registry and versioning
   - Artifact management
   - Reports and visualization
   - Multi-GPU/distributed training

2. Describe their concrete technical goal (e.g., "setting up experiment tracking across multiple GPUs" rather than just "using experiment tracking")

Format your response in 20-25 words following:

For clear technical goals:
"User needs help with [specific W&B feature] to [concrete technical goal], specifically [implementation detail/blocker]."

For general queries:
"User is asking about [W&B concept/feature] in the context of [relevant ML workflow/task]."

Reference the context below to identify the exact W&B functionality and technical requirements:
<context>
{{ context }}
</context>

Focus on technical specifics rather than general descriptions.
""",
                    },
                ],
                response_model=GeneratedSummary,
                context={"context": conversation.messages[0].content},
            )

            return ConversationSummary(
                chat_id=conversation.chat_id,
                summary=resp.summary,
                metadata={
                    "conversation_turns": len(conversation.messages),
                },
            )
```

We can now see the generated summaries by calling the `summarise` method below. We'll be using the same conversations above which we generated summaries for.

```python
summaries = await WnBSummaryModel().summarise(conversations[:2])
for summary in summaries:
    rprint(summary)

```

    Summarising 2 conversations: 100%|██████████| 2/2 [00:02<00:00,  1.44s/it]

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">ConversationSummary</span><span style="font-weight: bold">(</span>
    <span style="color: #808000; text-decoration-color: #808000">summary</span>=<span style="color: #008000; text-decoration-color: #008000">'User needs help with W&amp;B experiment tracking to record hyperparameters, log training metrics, and </span>
<span style="color: #008000; text-decoration-color: #008000">store model artifacts for ML experiments.'</span>,
    <span style="color: #808000; text-decoration-color: #808000">request</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">topic</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">languages</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">task</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">concerning_score</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">user_frustration</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">assistant_errors</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">chat_id</span>=<span style="color: #008000; text-decoration-color: #008000">'5e878c76-25c1-4bad-8cae-6a40ca4c8138'</span>,
    <span style="color: #808000; text-decoration-color: #808000">metadata</span>=<span style="font-weight: bold">{</span><span style="color: #008000; text-decoration-color: #008000">'conversation_turns'</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span><span style="font-weight: bold">}</span>,
    <span style="color: #808000; text-decoration-color: #808000">embedding</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>
<span style="font-weight: bold">)</span>
</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">ConversationSummary</span><span style="font-weight: bold">(</span>
    <span style="color: #808000; text-decoration-color: #808000">summary</span>=<span style="color: #008000; text-decoration-color: #008000">"User needs help with W&amp;B's hyperparameter optimization feature to implement Bayesian optimization for </span>
<span style="color: #008000; text-decoration-color: #008000">tuning model hyperparameters, specifically setting up the search space, performance metric, and run limit."</span>,
    <span style="color: #808000; text-decoration-color: #808000">request</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">topic</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">languages</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">task</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">concerning_score</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">user_frustration</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">assistant_errors</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>,
    <span style="color: #808000; text-decoration-color: #808000">chat_id</span>=<span style="color: #008000; text-decoration-color: #008000">'d7b77e8a-e86c-4953-bc9f-672618cdb751'</span>,
    <span style="color: #808000; text-decoration-color: #808000">metadata</span>=<span style="font-weight: bold">{</span><span style="color: #008000; text-decoration-color: #008000">'conversation_turns'</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span><span style="font-weight: bold">}</span>,
    <span style="color: #808000; text-decoration-color: #808000">embedding</span>=<span style="color: #800080; text-decoration-color: #800080; font-style: italic">None</span>
<span style="font-weight: bold">)</span>
</pre>

## Clustering with Enhanced Summaries

Now that we've developed a more domain-specific summarization approach tailored to the Weights & Biases ecosystem, we can apply these improved summaries to our clustering process.

Our custom `WnBSummaryModel` captures the specific features, workflows, and user intentions that were missing in the default summaries, providing a stronger foundation for meaningful topic discovery.

This will help us to reveal patterns in feature usage, common pain points and documentation gaps that might have been obscured in our analysis in our previous notebook. Let's see this in action below.

```python
from kura import (
    summarise_conversations,
    generate_base_clusters_from_conversation_summaries,
    reduce_clusters_from_base_clusters,
    reduce_dimensionality_from_clusters,
    CheckpointManager
)
from kura.cluster import ClusterModel
from kura.meta_cluster import MetaClusterModel
from kura.dimensionality import HDBUMAP



async def analyze_conversations(conversations, checkpoint_manager):
    # Set up models
    summary_model = WnBSummaryModel()
    cluster_model = ClusterModel()
    meta_cluster_model = MetaClusterModel(max_clusters=4)
    dimensionality_model = HDBUMAP()

    # Run pipeline steps
    summaries = await summarise_conversations(
        conversations,
        model=summary_model,
        checkpoint_manager=checkpoint_manager
    )

    clusters = await generate_base_clusters_from_conversation_summaries(
        summaries,
        model=cluster_model,
        checkpoint_manager=checkpoint_manager
    )

    reduced_clusters = await reduce_clusters_from_base_clusters(
        clusters,
        model=meta_cluster_model,
        checkpoint_manager=checkpoint_manager
    )

    projected = await reduce_dimensionality_from_clusters(
        reduced_clusters,
        model=dimensionality_model,
        checkpoint_manager=checkpoint_manager
    )

    return projected

checkpoint_manager = CheckpointManager("./checkpoints_2", enabled=True)
checkpoint_manager.save_checkpoint("conversations.jsonl", conversations)
clusters = await analyze_conversations(conversations, checkpoint_manager=checkpoint_manager)
```

```python
# Get top-level clusters (those without parents)
parent_clusters = [cluster for cluster in clusters if cluster.parent_id is None]

# Format each cluster's info with name, description and number of chats
formatted_clusters = []
for parent in parent_clusters:

    # Add parent cluster info
    cluster_info = (
        f"[bold]({parent.id}) {parent.name}[/bold] : {parent.description} : {len(parent.chat_ids)}\n"
    )

    # Get and format child clusters
    child_clusters = [c for c in clusters if c.parent_id == parent.id]
    for child in child_clusters:
        cluster_info += f"\n  • [bold]{child.name}[/bold] : {child.description} : {len(child.chat_ids)}"
        child_child_clusters = [c for c in clusters if c.parent_id == child.id]
        for child_child in child_child_clusters:
            if child_child.parent_id == child.id:
                cluster_info += f"\n    + [bold]{child_child.name}[/bold] : {child_child.description} : {len(child_child.chat_ids)}"

        cluster_info += "\n\n"

    formatted_clusters.append(cluster_info)
    formatted_clusters.append("\n====\n")

# Join with newlines and print
rprint("\n\n".join(formatted_clusters))
```

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-weight: bold">(3943254bfb5a471385aeadcc745e478b) Manage audio files and dataset versioning</span> : Users organized audio files for 
classification analysis and managed dataset versioning in W&amp;B. They focused on tasks such as loading metadata and 
updating datasets for effective machine learning workflows. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">37</span>

  • <span style="font-weight: bold">Organize audio files for classification analysis</span> : The user prepared and structured audio data for 
classification tasks. This included tasks like loading, merging, and synchronizing metadata for effective analysis.
: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2</span>
    + <span style="font-weight: bold">Prepare audio data for classification analysis</span> : The user processed and organized audio files for effective 
classification. This involved loading, merging DataFrames, and synchronizing metadata for analysis. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2</span>


  • <span style="font-weight: bold">Assist with dataset versioning in W&amp;B</span> : Users sought help with managing dataset versioning and artifacts in 
W&amp;B. They focused on logging, tracking, and updating datasets for improved reproducibility in machine learning 
workflows. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">35</span>
    + <span style="font-weight: bold">Help me manage dataset versioning in W&amp;B</span> : Users sought assistance with handling dataset versioning and 
artifacts in W&amp;B. They specifically focused on logging, tracking, and updating datasets for better reproducibility 
in their machine learning workflows. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">35</span>




====


<span style="font-weight: bold">(92d75e32975c4651a2ab46ccb8a83fd9) Optimize machine learning experiments and resources</span> : Users explored methods to 
optimize and visualize machine learning experiments through Weights &amp; Biases. They focused on hyperparameter 
tuning, multi-GPU training, and maximizing the tool's utilization for improved performance and efficiency. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">449</span>

  • <span style="font-weight: bold">Optimize and visualize machine learning experiments with W&amp;B</span> : Users explored methods to log and visualize 
machine learning experiments using Weights &amp; Biases. They focused on customizing visualizations, handling data 
formats, and enhancing tracking for better analysis. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">195</span>
    + <span style="font-weight: bold">Explore data visualization with W&amp;B Tables</span> : Users investigated how to visualize diverse media types using 
wandb.Table. They aimed to manage and analyze different data formats effectively within the W&amp;B Tables interface. :
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">4</span>
    + <span style="font-weight: bold">Help me log and visualize experiments in W&amp;B</span> : Users requested guidance on visualizing and logging various 
aspects of machine learning experiments using Weights &amp; Biases <span style="font-weight: bold">(</span>W&amp;B<span style="font-weight: bold">)</span>. They focused on customizing visualizations, 
tracking metrics, managing prompt configurations, and handling multi-class confusion matrices. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">71</span>
    + <span style="font-weight: bold">Enhance machine learning experiment tracking with W&amp;B</span> : Users optimized and troubleshot experiment tracking 
with Weights &amp; Biases, focusing on installation, configuration, and logging. They explored core features to improve
ML workflows, ensuring better collaboration and data analysis. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">120</span>


  • <span style="font-weight: bold">Assist with hyperparameter optimization using Weights &amp; Biases</span> : Users requested help with optimizing 
hyperparameters through Weights &amp; Biases. They sought guidance on configuring sweeps, automating processes, and 
analyzing results for better performance. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">60</span>
    + <span style="font-weight: bold">Help optimize hyperparameter sweeps using W&amp;B</span> : Users requested assistance in programmatically accessing and 
analyzing hyperparameter optimization results from W&amp;B sweeps. They sought guidance on optimizing configurations 
for efficient parallel training across multiple GPUs and CPUs. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">23</span>
    + <span style="font-weight: bold">Guide hyperparameter optimization using Weights &amp; Biases</span> : Users sought assistance with hyperparameter tuning
using Weights &amp; Biases and related tools. They requested support for configuring sweeps, automating processes, and 
troubleshooting to enhance performance. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">37</span>


  • <span style="font-weight: bold">Assist with multi-GPU training and optimization</span> : Users explored methods for effective multi-GPU distributed 
training using HuggingFace while seeking optimization of GPU resources during model training. They focused on job 
management, script arguments, and resource monitoring to enhance training efficiency. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">9</span>
    + <span style="font-weight: bold">Guide multi-GPU distributed training with HuggingFace</span> : Users requested help on setting up multi-GPU 
distributed training using HuggingFace Accelerate. They focused on launching jobs and managing script arguments 
across various hardware configurations. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3</span>
    + <span style="font-weight: bold">Optimize GPU resources for model training</span> : Users sought assistance in optimizing GPU usage and memory during
machine learning training. They emphasized the integration of W&amp;B for monitoring and enhancing the efficiency of 
training processes. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">6</span>


  • <span style="font-weight: bold">Assist in maximizing Weights &amp; Biases utilization</span> : Users sought guidance on using Weights &amp; Biases to manage 
experiments and data effectively. They aimed to optimize their machine learning workflows through understanding its
features, configurations, and best practices. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">185</span>
    + <span style="font-weight: bold">Guide effective use of Weights &amp; Biases</span> : Users sought assistance in leveraging Weights &amp; Biases for managing
experiments and data effectively. They aimed to enhance their machine learning workflows by understanding features,
configurations, and best practices related to experiment tracking, data manipulation, and artifact management. : 
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">185</span>




====


<span style="font-weight: bold">(126ad2b1c8054e7b93d0dc652841623c) Enhance machine learning project collaboration with W&amp;B</span> : Users integrated 
Weights &amp; Biases into machine learning workflows while enhancing team collaboration features. They focused on 
optimizing tracking, management settings, and collaborative capabilities for effective project execution. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">74</span>

  • <span style="font-weight: bold">Integrate W&amp;B with machine learning frameworks</span> : Users received help integrating W&amp;B tracking into their 
machine learning workflows, specifically with PyTorch and TensorFlow. They also learned to manage W&amp;B settings and 
SageMaker configurations for secure deployments and effective tracking. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">56</span>
    + <span style="font-weight: bold">Integrate W&amp;B tracking into ML workflows</span> : Users received assistance in integrating W&amp;B experiment tracking 
into their machine learning workflows using both PyTorch and TensorFlow. They learned to log metrics, 
hyperparameters, and artifacts effectively throughout the model training process. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">19</span>
    + <span style="font-weight: bold">Assist with W&amp;B and SageMaker setup tasks</span> : Users needed help configuring sharing settings for W&amp;B reports 
and managing API keys. They also sought assistance in setting up secure IAM roles for SageMaker to ensure safe 
deployment and access management. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">37</span>


  • <span style="font-weight: bold">Optimize team collaboration and management in W&amp;B</span> : Users explored ways to enhance collaboration and management
features in Weights &amp; Biases. They focused on configuring roles, permissions, and various enterprise capabilities 
for improved project outcomes. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">18</span>
    + <span style="font-weight: bold">Enhance team collaboration in Weights &amp; Biases</span> : Users sought to optimize collaborative features in Weights &amp;
Biases for better project management. They focused on configuring roles, permissions, and team settings to improve 
collaboration outcomes. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">10</span>
    + <span style="font-weight: bold">Help with team management and enterprise features</span> : Users sought assistance in managing team roles and 
permissions within W&amp;B, including inquiries about enterprise features specific to W&amp;B Server. They explored topics 
such as access control, secure storage, and distinctions in user management across membership tiers. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">8</span>




====

</pre>

## Conclusion

### What You Learned

In this notebook, you learned how to create domain-specific summarization models that dramatically improve clustering quality. You discovered how to:

- **Create custom summary models** using specialized prompts tailored to your domain
- **Replace generic descriptions** with precise, feature-specific summaries
- **Configure clustering parameters** to achieve optimal grouping results
- **Compare clustering outcomes** between default and custom approaches

### What We Accomplished

We built a custom `WnBSummaryModel` that addressed the key limitations from our initial clustering. By implementing domain-specific prompts that focus on W&B features and user intentions, we transformed our clustering results from generic topic groups into three highly actionable categories:

1. **Optimize machine learning experiments and resources** (449 conversations) - The largest cluster covering users exploring experiment tracking, hyperparameter optimization, multi-GPU training, and maximizing W&B utilization for improved ML performance
2. **Enhance machine learning project collaboration with W&B** (74 conversations) - Users integrating W&B with PyTorch/TensorFlow workflows and optimizing team collaboration features including roles, permissions, and enterprise capabilities
3. **Manage audio files and dataset versioning** (37 conversations) - Users organizing audio data for classification analysis and managing dataset versioning workflows in W&B

This represents a significant upgrade from our previous clusters, providing much more specific and actionable information about user needs. The improved summaries eliminated the vagueness of descriptions like "user seeks information about tracking" and replaced them with precise insights about specific W&B workflows, optimization goals, and collaboration requirements.

### Next: Building Production Classifiers

While our improved clustering gives us deep insights into historical query patterns, we need a way to act on these insights in real-time production environments. In the next notebook, "Classifiers", we'll bridge the gap between discovery and action by:

- **Building production-ready classifiers** using the `instructor` library that achieve 90.9% accuracy through systematic prompt engineering
- **Creating automated labeling workflows** with weak supervision to efficiently generate labeled datasets for training
- **Focusing on three high-impact categories** - artifacts (20% of queries), integrations (15%), and visualizations (14%) - that account for roughly 50% of all user conversations
- **Applying classifiers at scale** to understand true query distributions and identify exactly where to focus improvement efforts

This classifier will enable you to automatically categorize incoming queries in real-time, detect production drift when certain query types surge, and intelligently route questions to specialized retrieval systems. More importantly, you'll move from "we think users struggle with X" to "we know 20% of users need help with artifacts, 15% with integrations, and 14% with visualizations—and we can automatically detect and route these queries for specialized handling."

---

--8<--
"snippets/enrollment-button.md"
--8<--

---
