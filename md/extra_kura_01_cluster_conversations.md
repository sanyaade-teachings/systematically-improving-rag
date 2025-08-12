# Clustering Conversations: Discovering User Query Patterns

> **Series Overview**: This is the first notebook in a three-part series on systematically analyzing and improving RAG systems. We'll move from raw user queries to production-ready classifiers that enable data-driven improvements.

## Why This Matters

In large-scale RAG applications, you'll encounter thousands of user queries. Manually reviewing each is impossible, and simple keyword counting misses deeper patterns. **Topic modeling helps you systematically identify patterns in user queries**, giving you insights into what users are asking and how well your system serves them.

Topic modeling serves as the foundation for transforming raw user interactions into actionable insights by:

1. **Revealing clusters** of similar queries that might need specialized handling
2. **Providing evidence** for prioritizing improvements based on actual usage patterns
3. **Highlighting gaps** where your retrieval might be underperforming
4. **Creating a foundation** for building automated classification systems

While topic modeling isn't objective ground truth, it's an invaluable discovery tool that helps you understand where to focus limited engineering resources based on real user behavior rather than intuition.

## What You'll Learn

In this first notebook, you'll discover how to:

1. **Prepare Query Data for Analysis**
   - Format JSON data into Kura conversation objects
   - Structure query-document pairs with proper metadata
   - Set up data for effective clustering

2. **Run Hierarchical Topic Clustering**
   - Use Kura's procedural API for LLM-enhanced clustering
   - Generate meaningful summaries of conversation groups
   - Visualize the topic hierarchies that emerge

3. **Analyze and Interpret Results**
   - Examine cluster themes and distribution patterns
   - Identify high-impact areas for system improvements
   - Recognize limitations in default summarization

## What You'll Discover

**By the end of this notebook, you'll uncover that just three major topics account for over two-thirds of all user queries**, with artifact management appearing as a dominant theme across 61% of conversations. However, you'll also discover that default summaries are too generic, missing crucial details about specific W&B features—a limitation that motivates the custom summarization approach in the next notebook.

## What Makes Kura Different

Traditional topic modeling approaches like BERTopic or LDA rely purely on embeddings to group similar documents. **Kura enhances this process by leveraging LLMs to**:

1. **Generate Meaningful Summaries** - Create human-readable descriptions rather than just numeric vectors
2. **Extract Key Intents** - Identify specific user goals beyond surface-level keywords
3. **Build Topic Hierarchies** - Create multi-level trees showing relationships between themes

### Procedural API Design

Kura provides a clean procedural API that makes topic modeling accessible and composable. Rather than complex object hierarchies, you work with simple functions like:

- `summarise_conversations()` - Generate LLM summaries of conversations
- `generate_base_clusters_from_conversation_summaries()` - Create initial clusters
- `reduce_clusters_from_base_clusters()` - Merge similar clusters hierarchically
- `reduce_dimensionality_from_clusters()` - Project for visualization

This procedural approach makes it easy to customize individual steps, use checkpointing for long-running processes, and build reproducible pipelines while maintaining the flexibility to swap models and configurations.

By using LLMs for summarization before clustering, Kura produces more intuitive, actionable results than pure embedding-based approaches, setting the foundation for the systematic RAG improvement framework you'll build across this series.

## Understanding Topic Modeling

### What is Topic Modeling?

Topic modeling is a technique for automatically discovering themes or patterns in large collections of text. Think of it like sorting a massive pile of documents into folders based on what they're about—except the computer figures out both what the folders should be AND which documents belong in each one.

In the context of RAG systems, topic modeling helps us understand what types of questions users are asking without manually reading thousands of queries. Instead of just counting keywords (which misses context), topic modeling identifies semantically related queries that might use completely different words but ask about the same underlying concept.

### The Role of Embeddings

To group similar texts together, we first need to convert them into a format computers can compare. **Embeddings** are numerical representations of text—think of them as coordinates in a high-dimensional space where similar meanings are positioned closer together.

For example:

- "How do I version my model?" and "What's the best way to track model versions?" would have similar embeddings despite using different words
- These queries would be far from "How do I visualize training metrics?" in the embedding space

Modern embedding models (like those used by Kura) capture semantic meaning, not just surface-level word matches. This is why they're so powerful for understanding user intent.

### Making Sense with Dimensionality Reduction

Embeddings typically have hundreds or thousands of dimensions—impossible to visualize directly. **Dimensionality reduction** techniques compress these high-dimensional representations down to 2D or 3D while preserving the important relationships between points.

It's like creating a map of a globe—you lose some information when flattening 3D to 2D, but the relative positions of continents remain meaningful. Similarly, dimensionality reduction lets us visualize which queries cluster together, revealing the natural groupings in our data.

In this notebook, Kura handles these technical details for us, but understanding these concepts helps interpret why certain queries group together and how the clustering process works under the hood.

# Understanding Our Dataset

## Getting Started

To follow along with this tutorial, you'll need to set up your environment and download the necessary data. For complete setup instructions and to understand how this dataset was created, see the [Getting Started Tutorial](https://0d156a8f.kura-4ma.pages.dev/getting-started/tutorial/).

Quick setup:

```bash
export OPENAI_API_KEY="your_api_key"
git clone https://github.com/ivanleomk/kura.git
cd kura
curl -o conversations.json https://usekura.xyz/data/conversations.json
```

## Our Dataset

We're working with 560 real user queries from the Weights & Biases documentation, each manually labelled with a retrieved relevant document. This dataset gives us direct insight into how users interact with ML experiment tracking documentation.

By examining these query-document pairs, we gain valuable insights into:

- What information users actively seek and how they phrase questions
- Which documentation sections are most needed or confusing
- How different query patterns cluster together, revealing common user challenges

Topic modeling helps us identify semantically similar conversations, allowing us to group these queries into meaningful clusters that reveal broader patterns of user needs and pain points.

For anyone building RAG systems, this kind of dataset is gold. It helps you understand user intent, find gaps in your documentation, and prioritize improvements based on actual usage patterns rather than guesswork.

Without systematic analysis of such data, it's nearly impossible to identify patterns in how users interact with your system. Topic modeling gives us a data-driven way to improve retrieval strategies and function calling by understanding the most common user needs.

## Preparing Our Data

Before using Kura for topic modeling, we need to prepare our dataset. Each entry contains:

- `query`: The user's original question
- `matching_document`: The relevant document manually matched to this query
- `query_id`: Unique identifier for the query
- `matching_document_document_id`: ID of the matching document

Let's examine what this data looks like:

```python
import json

with open("./data/conversations.json") as f:
    conversations_raw = json.load(f)

conversations_raw[0]
```

    {'query_id': '5e878c76-25c1-4bad-8cae-6a40ca4c8138',
     'query': 'experiment tracking',
     'matching_document': '## Track Experiments\n### How it works\nTrack a machine learning experiment with a few lines of code:\n1. Create a W&B run.\n2. Store a dictionary of hyperparameters, such as learning rate or model type, into your configuration (`wandb.config`).\n3. Log metrics (`wandb.log()`) over time in a training loop, such as accuracy and loss.\n4. Save outputs of a run, like the model weights or a table of predictions.  \n\nThe proceeding pseudocode demonstrates a common W&B Experiment tracking workflow:  \n\n```python showLineNumbers\n\n# 1. Start a W&B Run\n\nwandb.init(entity="", project="my-project-name")\n\n# 2. Save mode inputs and hyperparameters\n\nwandb.config.learning\\_rate = 0.01\n\n# Import model and data\n\nmodel, dataloader = get\\_model(), get\\_data()\n\n# Model training code goes here\n\n# 3. Log metrics over time to visualize performance\n\nwandb.log({"loss": loss})\n\n# 4. Log an artifact to W&B\n\nwandb.log\\_artifact(model)\n```',
     'matching_document_document_id': '1c7f8798-7b2a-4baa-9829-14ada61db6bc',
     'query_weight': 0.1}

This raw format isn't immediately useful for topic modeling. We need to transform it into something that Kura can process effectively.

To do so, we'll convert it to a `Conversation` class which `Kura` exposes. This format allows Kura to:

1. Process the conversation flow (even though we only have single queries in this example)
2. Generate summaries of each conversation
3. Embed and cluster conversations based on content and structure

We'll create a function to convert each query-document pair into a Kura Conversation object with a single user Message that combines both the query and retrieved document.

```python
from kura.types import Message, Conversation
from datetime import datetime
from rich import print

def process_query_obj(obj:dict):
    return Conversation(
    chat_id=obj['query_id'],
    created_at=datetime.now(),
    messages=[
        Message(
            created_at=datetime.now(),
            role="user",
            content=f"""
User Query: {obj['query']}
Retrieved Information : {obj['matching_document']}
"""
            )
        ],
        metadata={
            'query_id': obj['query_id']
        }
    )


print(process_query_obj(conversations_raw[0]))
```

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">Conversation</span><span style="font-weight: bold">(</span>
    <span style="color: #808000; text-decoration-color: #808000">chat_id</span>=<span style="color: #008000; text-decoration-color: #008000">'5e878c76-25c1-4bad-8cae-6a40ca4c8138'</span>,
    <span style="color: #808000; text-decoration-color: #808000">created_at</span>=<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">datetime</span><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">.datetime</span><span style="font-weight: bold">(</span><span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2025</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">5</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">29</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">22</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">4</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">41</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">92552</span><span style="font-weight: bold">)</span>,
    <span style="color: #808000; text-decoration-color: #808000">messages</span>=<span style="font-weight: bold">[</span>
        <span style="color: #800080; text-decoration-color: #800080; font-weight: bold">Message</span><span style="font-weight: bold">(</span>
            <span style="color: #808000; text-decoration-color: #808000">created_at</span>=<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">datetime</span><span style="color: #800080; text-decoration-color: #800080; font-weight: bold">.datetime</span><span style="font-weight: bold">(</span><span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2025</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">5</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">29</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">22</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">4</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">41</span>, <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">92555</span><span style="font-weight: bold">)</span>,
            <span style="color: #808000; text-decoration-color: #808000">role</span>=<span style="color: #008000; text-decoration-color: #008000">'user'</span>,
            <span style="color: #808000; text-decoration-color: #808000">content</span>=<span style="color: #008000; text-decoration-color: #008000">'\nUser Query: experiment tracking\nRetrieved Information : ## Track Experiments\n### How it </span>
<span style="color: #008000; text-decoration-color: #008000">works\nTrack a machine learning experiment with a few lines of code:\n1. Create a W&amp;B run.\n2. Store a dictionary </span>
<span style="color: #008000; text-decoration-color: #008000">of hyperparameters, such as learning rate or model type, into your configuration (`wandb.config`).\n3. Log metrics </span>
<span style="color: #008000; text-decoration-color: #008000">(`wandb.log()`) over time in a training loop, such as accuracy and loss.\n4. Save outputs of a run, like the model </span>
<span style="color: #008000; text-decoration-color: #008000">weights or a table of predictions.  \n\nThe proceeding pseudocode demonstrates a common W&amp;B Experiment tracking </span>
<span style="color: #008000; text-decoration-color: #008000">workflow:  \n\n```python showLineNumbers\n\n# 1. Start a W&amp;B Run\n\nwandb.init(entity="", </span>
<span style="color: #008000; text-decoration-color: #008000">project="my-project-name")\n\n# 2. Save mode inputs and hyperparameters\n\nwandb.config.learning\\_rate = 0.01\n\n#</span>
<span style="color: #008000; text-decoration-color: #008000">Import model and data\n\nmodel, dataloader = get\\_model(), get\\_data()\n\n# Model training code goes here\n\n# 3.</span>
<span style="color: #008000; text-decoration-color: #008000">Log metrics over time to visualize performance\n\nwandb.log({"loss": loss})\n\n# 4. Log an artifact to </span>
<span style="color: #008000; text-decoration-color: #008000">W&amp;B\n\nwandb.log\\_artifact(model)\n```\n'</span>
        <span style="font-weight: bold">)</span>
    <span style="font-weight: bold">]</span>,
    <span style="color: #808000; text-decoration-color: #808000">metadata</span>=<span style="font-weight: bold">{</span><span style="color: #008000; text-decoration-color: #008000">'query_id'</span>: <span style="color: #008000; text-decoration-color: #008000">'5e878c76-25c1-4bad-8cae-6a40ca4c8138'</span><span style="font-weight: bold">}</span>
<span style="font-weight: bold">)</span>
</pre>

```python
conversations = [process_query_obj(obj) for obj in conversations_raw]
```

Each individual `Conversation` object exposes a metadata field which allows us to provide additional context that can be valuable for analysis.

In this case here, we add the Query ID to the metadata field so that we can preserve it for downstream processing. By properly structuring our data and enriching it with metadata, we're setting a strong foundation for the topic modeling work ahead.

This careful preparation will pay off when we analyze the results and turn insights into actionable improvements

## Running the Clustering Process

Now that we've converted our raw data into Kura's Conversation format, we're ready to run the clustering process. This is where we discover patterns across hundreds of conversations without needing to manually review each one.

We'll use Kura's procedural API to group similar conversations together, identify common themes, and build a hierarchical organization of topics. The clustering algorithm combines embedding similarity with LLM-powered summarization to create meaningful, interpretable results.

### The Clustering Pipeline

The hierarchical clustering process follows a systematic approach using Kura's procedural functions:

1. **Summarization**: `summarise_conversations()` - Each conversation is summarized by an LLM to capture its essence while removing sensitive details
2. **Embedding**: These summaries are converted into vector embeddings that capture their semantic meaning
3. **Base Clustering**: `generate_base_clusters_from_conversation_summaries()` - Similar conversations are grouped into small, initial clusters
4. **Hierarchical Merging**: `reduce_clusters_from_base_clusters()` - Similar clusters are progressively combined into broader categories
5. **Naming and Description**: Each cluster receives a descriptive name and explanation generated by an LLM
6. **Dimensionality Reduction**: `reduce_dimensionality_from_clusters()` - Projects clusters for visualization

### Procedural API Benefits

Kura's procedural design offers several advantages:

- **Composability**: Each function handles one step, making it easy to customize or replace individual components
- **Checkpointing**: Save intermediate results to avoid recomputing expensive operations
- **Transparency**: Clear function names make the pipeline easy to understand and debug
- **Flexibility**: Swap models or configurations without complex object management

By starting with many detailed clusters before gradually reducing them to more general topics, we preserve meaningful patterns while making results easy for humans to review.

```python
from kura import CheckpointManager

async def analyze_conversations(conversations, checkpoint_manager):
    from kura import (
        summarise_conversations,
        generate_base_clusters_from_conversation_summaries,
        reduce_clusters_from_base_clusters,
        reduce_dimensionality_from_clusters
    )
    from kura.summarisation import SummaryModel
    from kura.cluster import ClusterModel
    from kura.meta_cluster import MetaClusterModel
    from kura.dimensionality import HDBUMAP

    # Set up models
    summary_model = SummaryModel()
    cluster_model = ClusterModel()
    meta_cluster_model = MetaClusterModel()
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


checkpoint_manager = CheckpointManager("./checkpoints", enabled=True)
checkpoint_manager.save_checkpoint("conversations.jsonl", conversations)
clusters = await analyze_conversations(conversations, checkpoint_manager=checkpoint_manager)
```

In the output, we can see the consolidation process happening in real-time. Kura starts with 56 base clusters, then gradually merges them through multiple rounds until we reach 9 final top-level clusters. Each merge combines similar topics while preserving the essential distinctions between different conversation types.

Now, let's examine these top-level clusters to understand the main themes in our data.

By looking at the cluster names, descriptions, and sizes, we can quickly identify what users are discussing most frequently and how these topics relate to each other

```python
# Get top-level clusters (those without parents)
parent_clusters = [cluster for cluster in clusters if cluster.parent_id is None]

# Format each cluster's info with name, description and number of chats
formatted_clusters = []
for cluster in parent_clusters:
    cluster_info = (
        f"[bold]{cluster.name}[/bold] : {cluster.description} : {len(cluster.chat_ids)}"
    )
    formatted_clusters.append(cluster_info)

# Join with newlines and print
print("\n\n".join(formatted_clusters))
```

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><span style="font-weight: bold">Optimize security and management for data in AWS</span> : Users sought to improve security by clarifying IAM roles 
specific to AWS SageMaker training and by exploring best practices for dataset versioning. They also aimed to 
enhance data storage management strategies while addressing privacy concerns. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">75</span>

<span style="font-weight: bold">Enhance data management and team collaboration</span> : Users requested assistance with data tracking, table manipulation 
techniques, and improving team collaboration and project management. They sought guidance on collaboration metrics,
programming techniques, and best practices for managing project tasks effectively. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">67</span>

<span style="font-weight: bold">Guide on secure API key practices</span> : The user researched different strategies for safely managing API keys, 
emphasizing best practices in authentication and configuration. Key discussions included the use of environment 
variables and cloud secrets managers to enhance security measures. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">5</span>

<span style="font-weight: bold">Streamline ML logging and visualization enhancements</span> : Users sought guidance on effectively integrating and 
utilizing Weights &amp; Biases for machine learning logging and data analysis. They requested best practices for 
optimizing logging techniques, automating processes, and customizing visualizations to enhance their projects. : 
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">178</span>

<span style="font-weight: bold">Enhance machine learning performance and evaluation</span> : Users sought to improve machine learning models through 
hyperparameter optimization and logging metrics for accurate evaluations. They requested guidance on tools and 
libraries to assess model performance effectively. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">28</span>

<span style="font-weight: bold">Guide me on machine learning and Markdown usage</span> : Users received assistance in utilizing Markdown effectively for 
reports and troubleshooting machine learning tools. They sought guidance on configurations, training runs, and 
artifact management across various contexts. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">84</span>

<span style="font-weight: bold">Manage and log machine learning experiments efficiently</span> : Users focused on effective management and logging of 
machine learning experiments. They discussed techniques and specific tools like WandB to optimize performance and 
tracking. : <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">123</span>
</pre>

## Analysing Our Results

### Understanding Our Top-Level Clusters

Looking at the seven top-level clusters generated by Kura, we can identify clear patterns in how users are interacting with the documentation.

The three largest clusters account for 69% of all queries:

1. **Streamline ML logging and visualization enhancements** (178 conversations) - Users seeking guidance on integrating W&B for logging and customizing visualizations
2. **Manage and log machine learning experiments efficiently** (123 conversations) - Focus on experiment management and tracking using tools like WandB
3. **Guide me on machine learning and Markdown usage** (84 conversations) - Assistance with Markdown reports and troubleshooting ML tools

What's particularly notable is that **logging and experiment management dominate user concerns**. The top two clusters alone represent 54% of all queries (301 out of 560), both focusing on different aspects of experiment tracking and logging.

Additional significant themes include:

- **AWS integration and security** (75 conversations) - IAM roles, SageMaker training, and data storage
- **Team collaboration and data management** (67 conversations) - Table manipulation, collaboration metrics, and project management
- **Model performance optimization** (28 conversations) - Hyperparameter tuning and evaluation

This clustering reveals that the majority of user questions center around **how to effectively use W&B for logging, tracking, and visualizing ML experiments**. Users are consistently trying to figure out how to properly integrate W&B into their workflows, optimize their logging strategies, and create meaningful visualizations of their results.

### Analysing Our Summaries

Let's now examine what are some of the summaries that were generated by Kura for our individual query document pairs.

To do so, we'll read in the list of conversations that we started with and then find their corresponding summary. This will allows us to then evaluate how representative the conversation summary is of the individual conversation.

```python
from kura.types import ConversationSummary

checkpoint_manager = CheckpointManager("./checkpoints", enabled=True)
summaries = checkpoint_manager.load_checkpoint("summaries.jsonl", ConversationSummary)
conversations = checkpoint_manager.load_checkpoint("conversations.jsonl", Conversation)


id_to_conversation = {
    conversation.chat_id: conversation
    for conversation in conversations
}



for i in range(3):
    print(summaries[i].summary)
    print(id_to_conversation[summaries[i].chat_id].messages[0].content)
```

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">The user is seeking guidance on tracking machine learning experiments using a specific tool, detailing the steps 
and providing pseudocode for implementation.
</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
User Query: experiment tracking
Retrieved Information : ## Track Experiments
### How it works
Track a machine learning experiment with a few lines of code:
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>. Create a W&amp;B run.
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2</span>. Store a dictionary of hyperparameters, such as learning rate or model type, into your configuration 
<span style="font-weight: bold">(</span>`wandb.config`<span style="font-weight: bold">)</span>.
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3</span>. Log metrics <span style="font-weight: bold">(</span>`<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.log</span><span style="font-weight: bold">()</span>`<span style="font-weight: bold">)</span> over time in a training loop, such as accuracy and loss.
<span style="color: #008080; text-decoration-color: #008080; font-weight: bold">4</span>. Save outputs of a run, like the model weights or a table of predictions.  

The proceeding pseudocode demonstrates a common W&amp;B Experiment tracking workflow:  

```python showLineNumbers

# <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">1</span>. Start a W&amp;B Run

<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.init</span><span style="font-weight: bold">(</span><span style="color: #808000; text-decoration-color: #808000">entity</span>=<span style="color: #008000; text-decoration-color: #008000">""</span>, <span style="color: #808000; text-decoration-color: #808000">project</span>=<span style="color: #008000; text-decoration-color: #008000">"my-project-name"</span><span style="font-weight: bold">)</span>

# <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">2</span>. Save mode inputs and hyperparameters

wandb.config.learning\_rate = <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">0.01</span>

# Import model and data

model, dataloader = get\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_model</span><span style="font-weight: bold">()</span>, get\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_data</span><span style="font-weight: bold">()</span>

# Model training code goes here

# <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">3</span>. Log metrics over time to visualize performance

<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.log</span><span style="font-weight: bold">({</span><span style="color: #008000; text-decoration-color: #008000">"loss"</span>: loss<span style="font-weight: bold">})</span>

# <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">4</span>. Log an artifact to W&amp;B

wandb.log\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_artifact</span><span style="font-weight: bold">(</span>model<span style="font-weight: bold">)</span>
```

</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">Bayesian optimization is a hyperparameter tuning technique that uses a surrogate function for informed search, 
contrasting with grid and random search methods.
</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
User Query: Bayesian optimization
Retrieved Information : ## Methods for Automated Hyperparameter Optimization
### Bayesian Optimization
Bayesian optimization is a hyperparameter tuning technique that uses a surrogate function to determine the next set
of hyperparameters to evaluate. In contrast to grid search and random search, Bayesian optimization is an informed 
search method.  

### Inputs  

* A set of hyperparameters you want to optimize
* A continuous search space for each hyperparameter as a value range
* A performance metric to optimize
* Explicit number of runs: Because the search space is continuous, you must manually stop the search or define a 
maximum number of runs.  

The differences in grid search are highlighted in bold above.  

A popular way to implement Bayesian optimization in Python is to use BayesianOptimization from the 
<span style="font-weight: bold">(</span><span style="color: #0000ff; text-decoration-color: #0000ff; text-decoration: underline">https://github.com/fmfn/BayesianOptimization)</span> library. Alternatively, as shown below, you can set up Bayesian 
optimization for hyperparameter tuning with W&amp;B.  

### Steps  

### Output  

### Advantages  

### Disadvantages

</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">The user seeks guidance on integrating a specific tool with a programming framework for tracking machine learning 
experiments. The conversation includes pseudocode for implementation steps.
</pre>

<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">
User Query: How to integrate Weights &amp; Biases with PyTorch?
Retrieved Information : ## 🔥 = W&amp;B ➕ PyTorch

Use Weights &amp; Biases for machine learning experiment tracking, dataset versioning, and project collaboration.  

## What this notebook covers:  

We show you how to integrate Weights &amp; Biases with your PyTorch code to add experiment tracking to your pipeline.  

## The resulting interactive W&amp;B dashboard will look like:  

## In pseudocode, what we'll do is:  

```
# import the library
import wandb

# start a new experiment
<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.init</span><span style="font-weight: bold">(</span><span style="color: #808000; text-decoration-color: #808000">project</span>=<span style="color: #008000; text-decoration-color: #008000">"new-sota-model"</span><span style="font-weight: bold">)</span>

# capture a dictionary of hyperparameters with config
wandb.config = <span style="font-weight: bold">{</span><span style="color: #008000; text-decoration-color: #008000">"learning\_rate"</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">0.001</span>, <span style="color: #008000; text-decoration-color: #008000">"epochs"</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">100</span>, <span style="color: #008000; text-decoration-color: #008000">"batch\_size"</span>: <span style="color: #008080; text-decoration-color: #008080; font-weight: bold">128</span><span style="font-weight: bold">}</span>

# set up model and data
model, dataloader = get\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_model</span><span style="font-weight: bold">()</span>, get\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_data</span><span style="font-weight: bold">()</span>

# optional: track gradients
<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.watch</span><span style="font-weight: bold">(</span>model<span style="font-weight: bold">)</span>

for batch in dataloader:
metrics = model.training\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_step</span><span style="font-weight: bold">()</span>
# log metrics inside your training loop to visualize model performance
<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.log</span><span style="font-weight: bold">(</span>metrics<span style="font-weight: bold">)</span>

# optional: save model at the end
model.to\<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">_onnx</span><span style="font-weight: bold">()</span>
<span style="color: #800080; text-decoration-color: #800080; font-weight: bold">wandb.save</span><span style="font-weight: bold">(</span><span style="color: #008000; text-decoration-color: #008000">"model.onnx"</span><span style="font-weight: bold">)</span>

```  

## Follow along with a video tutorial!

</pre>

## Conclusion

### What You Learned

In this notebook, you discovered how to transform raw user queries into actionable insights for RAG system improvements. You learned to:

- **Prepare query data for Kura** by formatting JSON data into Conversation objects with proper metadata
- **Run hierarchical clustering** using Kura's built-in capabilities to group similar conversations
- **Analyze clustering results** to identify the most common user query patterns and pain points

### What We Accomplished

By leveraging Kura's clustering capabilities, we organized 560 user queries into nine meaningful clusters that revealed clear patterns in how users interact with Weights & Biases documentation. The analysis showed that three major topics—experiment tracking, tool integration, and artifact management—account for over two-thirds of all queries, with artifact management appearing as a significant theme across multiple clusters (61% of conversations).

However, we also identified critical limitations in the default summarization approach. Our generated summaries lacked specificity about the tools users wanted to use and sometimes included irrelevant context from retrieved documents. For example, summaries described queries as "user seeks information about tracking" rather than capturing the specific W&B features involved.

### Next: Better Summaries

While our clustering revealed valuable high-level patterns, the generic summaries limit our ability to understand specific user needs. In the next notebook, "Better Summaries", we'll address this limitation by building a custom summarization model that:

- **Identifies specific W&B features** (Artifacts, Configs, Reports) mentioned in each query
- **Captures precise user intent** rather than generic descriptions
- **Creates domain-specific summaries** tailored to W&B terminology and workflows

By replacing vague summaries like "user seeks information about tracking" with precise descriptions like "user is managing W&B Artifacts for model versioning", we'll create clusters that better reflect real user needs and provide more targeted, actionable insights for system improvements.

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
