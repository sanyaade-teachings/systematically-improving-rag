---
title: Workshops
description: Hands-on workshops for building self-improving RAG systems
---

# Workshops

This series of workshops guides you through the complete process of building, evaluating, and continuously improving RAG systems. Learn how to transform your RAG implementation from a static technical deployment into a continuously evolving product that systematically improves through user feedback and data-driven enhancement.

## Detailed Table of Contents

### [Introduction: Beyond Implementation to Improvement](chapter0.md)
**The Product Mindset for RAG Systems**

- Shifting from technical implementation to product-focused continuous improvement
- Understanding RAG as a recommendation engine wrapped around language models
- The improvement flywheel: transforming user interactions into system enhancements
- Moving from ad-hoc tweaking to systematic, data-driven improvement
- Case studies showing the difference between implementation and product mindsets

### [Chapter 1: Kickstarting the Data Flywheel with Synthetic Data](chapter1.md)
**Establishing Evaluation Frameworks and Overcoming the Cold Start Problem**

- Common pitfalls in AI development: reasoning fallacy, vague metrics, generic solutions
- Leading vs. lagging metrics: focusing on controllable inputs like experiment velocity
- Understanding precision and recall for retrieval evaluation
- Synthetic data generation techniques using chain-of-thought and few-shot prompting
- Building evaluation pipelines that run continuously
- Case studies: improving recall from 50% to 90% through systematic evaluation

### [Chapter 2: Converting Evaluations into Training Data for Fine-Tuning](chapter2.md)
**From Evaluation to Production Improvement**

- Why generic embeddings fall short for specialized applications
- Converting evaluation examples into effective few-shot prompts
- Understanding contrastive learning and hard negative mining
- Fine-tuning embedding models vs. language models: cost, complexity, and benefits
- Building training datasets from user interactions and feedback
- Re-rankers and linear adapters as cost-effective enhancement strategies

### Chapter 3: User Experience and Feedback Collection

#### [Chapter 3.1: Feedback Collection - Building Your Improvement Flywheel](chapter3-1.md)
**Designing Feedback Mechanisms That Users Actually Use**

- Making feedback visible and engaging: increasing rates from <1% to >30%
- Proven copy patterns: "Did we answer your question?" vs. generic feedback
- Segmented feedback targeting specific pipeline components
- Mining implicit feedback: query refinements, engagement time, citation clicks
- Creative UI patterns for collecting hard negatives
- Enterprise feedback collection through Slack integrations

#### [Chapter 3.2: Overcoming Latency - Streaming and Interstitials](chapter3-2.md)
**Transforming Waiting Time into Engagement Opportunities**

- Psychology of waiting: perceived vs. actual performance
- Implementing streaming responses for 30-40% higher feedback collection
- Skeleton screens and meaningful interstitials
- Platform-specific implementations: Slack bots, web interfaces
- Technical implementation: Server-Sent Events, structured data streaming
- Streaming function calls and reasoning processes

#### [Chapter 3.3: Quality of Life Improvements](chapter3-3.md)
**Citations, Chain of Thought, and Validation Patterns**

- Interactive citations that build trust while collecting feedback
- Chain of thought reasoning for 8-15% accuracy improvements
- Monologues for better comprehension in complex contexts
- Validation patterns as safety nets: reducing errors by 80%
- Strategic rejection of work to set appropriate expectations
- Showcasing capabilities to guide users toward successful interactions

### Chapter 4: Understanding Your Users Through Data Analysis

#### [Chapter 4.1: Topic Modeling and Analysis](chapter4-1.md)
**Finding Patterns in User Feedback and Queries**

- Moving from individual feedback to systematic pattern identification
- Topics vs. capabilities: understanding what users ask about vs. what they want the system to do
- Clustering and classification techniques for query segmentation
- Transforming "make the AI better" into specific, actionable priorities
- Resource allocation frameworks for maximum impact improvements

#### [Chapter 4.2: Prioritization and Roadmapping](chapter4-2.md)
**From Insights to Strategic Action Plans**

- Impact/effort prioritization using 2x2 frameworks
- Failure mode analysis: identifying root causes vs. symptoms
- Building strategic roadmaps based on user behavior patterns
- Continuous improvement systems that scale with usage
- Case studies: how query analysis changes development priorities

### Chapter 5: Building Specialized Retrieval Capabilities

#### [Chapter 5.1: Understanding Specialized Retrieval](chapter5-1.md)
**Beyond Basic RAG: The Power of Specialization**

- Why monolithic approaches reach limits with diverse query types
- Two complementary strategies: extracting metadata vs. creating synthetic text
- Mathematics of specialization: local models outperforming global approaches
- Organizational benefits: division of labor and incremental improvement
- Two-level measurement: router accuracy × retriever performance

#### [Chapter 5.2: Implementing Multimodal Search](chapter5-2.md)
**Practical Techniques for Documents, Images, Tables, and SQL**

- Advanced document retrieval: contextual chunks, page-level strategies, hybrid signals
- Image search challenges: bridging visual and textual understanding with rich descriptions
- Table search dual approach: tables as documents vs. queryable databases
- SQL generation using RAG playbook: inventory → exemplars → business context
- RAPTOR hierarchical summarization for complex documents
- Performance improvements: 40% better image retrieval, 85% table lookup accuracy

### Chapter 6: Unified Architecture and Intelligent Routing

#### [Chapter 6.1: Query Routing Foundations](chapter6-1.md)
**Building Cohesive Systems from Specialized Components**

- The API mindset: treating retrievers as services for language models
- Organizational structure: interface, implementation, router, and evaluation teams
- Evolution from monolithic to modular architecture
- Performance formula: P(success) = P(right tool) × P(right document | right tool)
- Framework development perspective for distributed RAG systems

#### [Chapter 6.2: Tool Interfaces and Implementation](chapter6-2.md)
**Implementing Routing Layers and Tool Selection**

- Designing tool interfaces with Pydantic models and comprehensive documentation
- Router implementation using structured outputs and few-shot examples
- Dynamic example selection based on query similarity
- Multi-agent vs. single-agent architecture decisions
- Tool portfolio design: multiple access patterns for same data
- MCP (Model Context Protocol) as emerging standard

#### [Chapter 6.3: Performance Measurement and Improvement](chapter6-3.md)
**Building Learning Systems That Continuously Improve**

- Measuring tool selection effectiveness: precision, recall, confusion matrices
- Dual-mode UI: chat interface + direct tool access
- User feedback as high-quality training data
- Diagnostic frameworks for identifying routing vs. retrieval problems
- Automated evaluation pipelines and continuous monitoring
- Creating improvement flywheel: interactions → data → better routing → higher satisfaction

## Workshop Structure

Each workshop combines theoretical concepts with practical exercises that you can apply directly to your own RAG implementations. Workshops are designed to be completed sequentially, as each one builds on concepts from previous sessions.

The workshops follow a complete methodology:

1. **Foundation** (Introduction & Chapter 1): Product mindset and evaluation frameworks
2. **Improvement Mechanics** (Chapter 2): Converting evaluation into training data  
3. **User Experience** (Chapter 3): Feedback collection, streaming, and quality improvements
4. **Analysis** (Chapter 4): Understanding user patterns and prioritizing improvements
5. **Specialization** (Chapter 5): Building specialized capabilities for different content types
6. **Unification** (Chapter 6): Intelligent routing and unified architecture

!!! note "Prerequisites"
    These workshops assume basic familiarity with RAG implementations and foundational AI concepts. If you're new to RAG, we recommend reviewing the [Introduction](chapter0.md) before diving into the other chapters.

!!! success "What You'll Build"
    By completing this workshop series, you'll have built a comprehensive RAG system that:
    
    - Continuously improves through systematic feedback collection
    - Routes queries intelligently to specialized retrieval components  
    - Provides engaging user experiences with streaming and transparency
    - Uses data-driven prioritization for enhancement decisions
    - Implements validation patterns and quality safeguards
    - Scales across teams and complexity levels

## Newsletters

If you want to get the latest news and updates, you can subscribe to our newsletter.

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
