---
title: Course Promo — Systematically Improving RAG
type: Promo
description: Strong hooks and sample questions drawn from Cohort 3 office hours
---

## Stop guessing — build RAG systems that ship

Turn real user data into better retrieval, better reasoning, and better business outcomes. This course helps you move past demos and build systems that are measurable, reliable, and valuable.

### Subject line options

- Stop guessing. Build RAG systems that get better every week
- From demo to durable: a product mindset for RAG
- The RAG improvement flywheel your team actually needs

#### Preheader

Turn your RAG into a product that improves with real user data, not a one-off project.

#### Email intro

Most teams ship a RAG demo, celebrate, then watch it stall in production. The problem isn’t your embedding model or context window. It’s the mindset. If you treat RAG as a one-time implementation, it dies. Treat it like a product with feedback and you ship improvements every week.

This course shows you how to move from “make the AI better” to a concrete, repeatable system. We reframe RAG as a recommendation engine wrapped around an LLM—then give you the improvement flywheel to make it work in the real world.

#### What you’ll learn to do

- Understand vs. guess: set up retrieval-first evals and K-sweeps so choices are data-driven
- Start before users: generate synthetic queries to beat cold start, then lock a rubric with small human audits
- Get the right feedback: add streaming, interstitials, and visible prompts to 3–5× feedback rates
- Learn from users: segment queries, find high-value patterns, and prioritize with an expected-value model
- Go specialized: build indices that match real tasks (lexical, semantic, SQL, tables, images)
- Route with confidence: expose tools as APIs and measure P(success) end to end
- Ship responsibly: watch drift, freshness, cost, and regressions with simple guardrails

## What you’ll learn

- Precision vs recall you can measure and tune
- Retrieval architectures that actually work in production
- Data strategies: hard negatives, summaries at ingestion, fine-tuning
- Tool portfolios and agents that beat single semantic search
- Temporal reasoning for medical and other timeline-heavy domains
- Pricing and evaluation tied to business value, not just tokens

### Workshops: what you’ll build

#### Chapter 1 — Synthetic evals that find your bottlenecks

You’ll spin up a retrieval‑first evaluation harness before you have users. Generate realistic synthetic queries, build recall@K tests, and sweep K to set thresholds from data, not vibes. Plot precision/recall curves and track them in a lightweight dashboard. Use an LLM‑as‑judge carefully to filter chunks and seed queries, then lock the rubric with a small human‑labeled set. Automate a nightly job so regressions surface immediately.

##### Learning outcomes — Chapter 1

- Define leading vs lagging metrics for your RAG (Remember → Understand)
- Implement a retrieval eval harness and compute recall@K on ≥100 queries (Apply)
- Analyze K‑sweep charts and justify a K threshold with an elbow criterion (Analyze → Evaluate)
- Calibrate an LLM‑as‑judge rubric to ≥0.8 agreement on a 50‑sample audit (Evaluate)
- Automate nightly evals and publish a dashboard to detect regressions (Create)

#### Chapter 2 — Turn eval data into better models

Convert failures into training data: start with few‑shot prompts, then fine‑tune embeddings or a re‑ranker. Build a tiny training pipeline (dozens → hundreds of examples) and compare latency/recall/MRR against your evals. Track cost and wall‑clock time so wins are practical. Use hard negatives from near‑miss retrievals and user deletions. Re‑run your evals to verify real, end‑to‑end gains.

##### Learning outcomes — Chapter 2

- Construct a hard‑negative mining pipeline from logs and near‑misses (Create)
- Fine‑tune an embedding or re‑ranker and report recall@K/MRR vs baseline (Apply → Evaluate)
- Estimate cost/latency trade‑offs and recommend a model choice with justification (Evaluate)
- Deploy behind a flag and verify end‑to‑end gains on your eval suite (Apply)

#### Chapter 3 — Feedback flywheel and UX that feels fast

Add visible, contextual feedback prompts that lift response rates; mine implicit signals from regenerations and follow‑ups. Implement streaming (SSE), skeletons, and interstitials to boost perceived speed and feedback volume. Ship interactive citations, chain‑of‑thought where appropriate, and simple validators to catch obvious errors before users see them. Measure edit/regenerate rates to close the loop.

##### Learning outcomes — Chapter 3

- Design and ship a feedback UI that increases submissions ≥3× vs baseline (Create → Evaluate)
- Implement SSE streaming and reduce regenerate rate by ≥20% (Apply → Evaluate)
- Add interactive citations and capture delete/regenerate as signals (Apply)
- Implement pre‑flight validators that halve trivial formatting/citation errors (Apply → Evaluate)

#### Chapter 4 — Segment users and pick what to build next

Cluster and label queries to create actionable segments; build a lightweight classifier to route new traffic. Use the volume × satisfaction × expected‑value quadrants to prioritize work. Instrument segment‑level metrics (retry rate, time‑to‑success) so improvements are attributable. Turn this into an explicit roadmap that ties to business goals.

##### Learning outcomes — Chapter 4

- Cluster queries and produce 10–20 segments covering ≥80% of traffic (Analyze)
- Build a few‑shot or simple classifier with ≥80% label agreement on 100 queries (Apply → Evaluate)
- Prioritize segments with an expected‑value formula and publish a roadmap (Evaluate → Create)
- Instrument segment metrics (retry, time‑to‑success) and show movement after fixes (Analyze → Evaluate)

#### Chapter 5 — Specialized retrieval that actually works

Define indices per capability (lexical, semantic, SQL, image/table). Choose between extracting metadata vs synthesizing summary chunks; test both. Implement page‑aware chunking for docs, markdown tables for tabular reasoning, and task‑aware summaries for recall. Measure per‑index precision/recall and keep synthetic summaries as pointers to sources.

##### Learning outcomes — Chapter 5

- Design at least three specialized indices and document their schemas (Create)
- Implement page‑aware chunking and improve passage‑level recall by ≥10 pp on a doc set (Apply → Evaluate)
- Represent tabular/temporal data in Markdown tables and validate lookup accuracy (Apply → Evaluate)
- Generate task‑aware summaries that cut tokens ≥30% with stable recall (Analyze → Evaluate)

#### Chapter 6 — Route to the right tool and prove it

Expose tools as clean APIs (Pydantic schemas), then build a router with few‑shot examples and dynamic selection. Log plans and tool outcomes to iterate routing accuracy. Measure with the chain rule: P(success) = P(right tool) × P(find right doc | right tool). Add dual‑mode UIs (chat + direct tool access) to debug quickly.

##### Learning outcomes — Chapter 6

- Define Pydantic tool interfaces and a router with few‑shot selection (Create)
- Measure P(success) and increase it by ≥15 pp via routing or tool fixes (Analyze → Evaluate)
- Add a dual‑mode UI (chat + direct tool) to diagnose routing errors faster (Apply)
- Compare single‑agent vs multi‑agent for your case and justify architecture (Evaluate)

#### Chapter 7 — Make it production‑ready

Track token economics (most cost is generation), and decide where to spend compute (write‑time vs read‑time). Add monitoring for cosine distance drift, re‑ranker score distributions, and feedback ratios. Set up security, staleness checks, and failure playbooks. Keep the eval suite in CI to prevent regressions.

##### Learning outcomes — Chapter 7

- Instrument drift/staleness metrics and set alert thresholds (Apply)
- Compute cost per answer and reduce by ≥20% without quality loss (Analyze → Evaluate)
- Implement freshness SLAs for indices and automated backfills (Apply)
- Integrate evals into CI to block regressions on critical metrics (Create)

## Format

- 6 weeks, with live office hours and guest speakers
- Hands-on notebooks and practical frameworks
- Ongoing Slack access after the cohort ends

## Who it’s for

- Engineers, PMs, founders, and data scientists shipping AI into production

## Outcomes

- Ship features that improve measurable metrics (precision, recall, latency, cost)
- Build retrieval that holds up to real usage
- Tie model choices and tooling to business results

## Questions we answer during office hours

### Evaluation and metrics

#### How should we understand precision vs recall in RAG, and where should we set K?

Start by sweeping K and plotting precision and recall together on a held‑out eval set that matches your production queries. Look for the elbow where recall gains flatten but precision drops if you add more documents. Older models are more sensitive to low‑precision context, but even newer models can pick up red herrings when you over‑stuff context. Validate not only exact‑match metrics but also factuality and citation correctness as K increases. Re‑run this sweep whenever your corpus or embedding changes because the optimal K will move. In practice, teams often land between 5 and 20 docs, but your data distribution should drive the choice.

#### What metrics should we monitor for retrieval quality in production?

Monitor average cosine distance per query over time and alert on shifts by user segment, product area, or market. Track re‑ranker score distributions and top‑K overlap stability to detect corpus drift or indexing regressions. Add user‑behavior signals like regenerate rate, citation deletions, and document dismissals as implicit labels. Watch retrieval depth (how often answers come from ranks 1–3 vs 4–10) to spot quality regressions early. Build dashboards that compare cohorts before/after releases and by data freshness. Changes and trends matter more than absolute numbers when the environment is non‑stationary.

#### How should we approach end-to-end evaluation of complex RAG systems?

Break the problem into stages: retrieval adequacy (did we fetch the right evidence?), reasoning correctness (given the evidence, is the chain of thought valid?), and output quality (is the answer clear, cited, and actionable?). For tool‑based systems, evaluate plan quality before execution and measure plan acceptance rates. Maintain small gold sets per domain and keep hardening them with new edge cases as your system improves. Include SLA metrics—latency, cost per answer, and stability—because product viability depends on them. Use error taxonomies to tag failures (missing evidence vs misuse vs formatting) so fixes map to clear owners. For periodic health checks, run a mixed suite of synthetic and real queries.

#### How should we use LLM‑as‑a‑judge with rubrics?

For complex outputs like reports and multi‑turn flows, define a clear rubric with explicit criteria and have an LLM score each criterion (e.g., 0–4). Calibrate these scores against a small human‑labeled gold set and aggregate with a simple, explainable model (like logistic regression) so you can see which features drive the decision. Ensembles help: sample multiple graders and use majority voting or averaged scores to increase stability. LLM‑as‑judge excels at checking whether required elements are present; nuanced quality still benefits from targeted human review. Keep prompts, examples, and edge‑case anchors consistent to control drift over time. Use the judge both offline (to grow eval sets) and online (to flag regressions and label user feedback at scale).

### Retrieval and architecture

#### What’s the right chunking strategy for docs—page-level vs token-based?

For technical manuals and PDFs, page‑level chunks work well because authors structure information with headings and figures per page. Combine BM25 (lexical) with embeddings to catch both exact terms and semantic matches. Preserve headers and figure captions so retrieval points users to the right visual context. Only split pages further when they exceed context limits or mix unrelated content. Validate with task‑based evals—“find the page” is often the real job‑to‑be‑done. Keep page metadata (section, chapter) for better filtering and UI breadcrumbs.

#### Should we use graph-based RAG, or will SQL + embeddings win in practice?

Most production use cases don’t need a full graph layer; a relational database with good schemas and embeddings handles the majority of joins. Graphs add modeling and query‑language overhead, and building taxonomies is slower than teams expect. Use graphs when you truly need multi‑hop traversals with variable depth or when relationships are the primary data. Otherwise, keep data in SQL, add indices, and expose specialized queries as tools. This keeps latency low and the system maintainable by a broader team. Evaluate complexity against measurable gains before adopting graph infra.

#### How should we allocate compute: contextual retrieval at write-time vs traversal at read-time?

Contextual retrieval rewrites chunks at indexing time to include key entities and links, trading more write‑time compute for faster reads. Traversal keeps chunks minimal and assembles context at query time, which is flexible but can feel slower. If your corpus is stable and latency is critical (e.g., clinical settings), invest compute at write time and cache aggressively. If your data is evolving or you need rich, ad‑hoc exploration, traversal pays off. Many teams mix both: contextualize frequent tasks, traverse for long tail queries. Always test the user‑perceived latency, not just backend timings.

#### Postgres + pgvector vs specialized vector DBs—what actually matters?

Postgres + pgvector gives you vectors, SQL joins, and permission filters in one place, which simplifies real apps. Add pg_search or equivalent BM25 to combine lexical and semantic signals. At very large scale, consider pgvector_scale for exhaustive search or an ANN index tuned for your recall target. A single database reduces operational complexity vs stitching services together. Specialized vector DBs can help at extreme scales or with niche features, but prove the need with load tests. Optimize for total system simplicity and observability, not just top‑1 recall on a micro‑benchmark.

### Data, training, and quality

#### Which open-source re-rankers and embeddings are worth fine-tuning?

Start with BGE models (embeddings and re‑rankers); they train stably with standard tooling and have predictable curves. Build a small harness to compare latency, recall@K, and MRR on your queries before committing. Favor models your team can reliably fine‑tune and host within your constraints (on‑prem, memory, batch size). Keep hyperparameters boring until your dataset is solid—data quality beats clever schedules. Track inference cost and throughput, not just accuracy. Revisit choices quarterly as libraries and weights improve.

#### How do we create high-signal hard negatives from real user behavior?

Generate near‑miss negatives by retrieving the most similar items from different classes so the model learns real boundaries. Capture product signals: deleted citations, “regenerate without doc X,” skipped recommendations, and returns after purchase. These edge cases are far more instructive than random negatives. Store them with rich metadata (time, user segment, tool used) for targeted training. Refresh your hard‑negative pool frequently so training tracks current failure modes. Expect 20–30% gains from good negatives vs 5–6% from naive data increases.

#### Can fine-tuning drive citation error rates to near-zero—and how much data is needed?

Yes—when the goal is formatting and alignment (not new knowledge), focused fine‑tunes can cut citation errors to near zero. Start with ~1,000 validated examples and scale only if the curve hasn’t flattened. Shuffle source order to reduce position bias unless your retriever sorts by relevance and you want the model to respect it. Validate on a strict held‑out set with substring checks and span boundaries. Add failure examples where paraphrases still point to the correct span. Re‑train periodically as your prompt and retriever evolve.

#### How can document summaries at ingestion boost recall and latency?

Create task‑aware summaries during ingestion that extract the fields users actually ask for. Index these summaries separately and search them first; they act like compressed views of your corpus. This improves hit rates on small context models and cuts token usage on large ones. Design prompts per domain (e.g., count rooms and sizes for blueprints, list decisions and dates for meetings). Measure recall improvements and latency savings—teams see double‑digit recall gains quickly. Keep original text accessible for grounding and quoting.

### Tools, agents, and UX

#### When does a portfolio of specialized tools beat single semantic search?

As soon as queries need structured filters, entity resolution, or non‑text sources, a toolkit beats one search box. Expose tools like “contact_search,” “contract_by_rfi,” and “date_range_filter” with clear descriptions. Have the model write a plan listing which tools it will call and in what order. Log plan acceptance and tool success to refine routing. This creates clean supervision data without heavy labeling. You’ll see fewer retries, more consistent answers, and better user trust.

#### Multi-agent vs single-agent: when is coordination worth the cost?

Multi‑agent shines when the task is read‑only research and you benefit from parallel, larger total token budgets. Single‑agent is safer when edits or code changes must be coordinated—shared state is hard. You can mix both: multiple read‑only researchers feed a single editor/decider. Evaluate quality vs latency: more agents can mean more overhead if you reduce poorly. Add guardrails to ensure nothing critical is dropped during reduction. Choose the simplest design that meets quality and SLA targets.

#### How do we add dynamic visuals (Mermaid, charts, screenshots) to AI reports—and validate them?

Treat visuals as first‑class outputs: let the model propose diagrams and images, then validate before rendering. For Mermaid, compile and capture errors to trigger an iterative fix loop. Treat screenshots and images like citations with source IDs and bounding boxes. Use a small charting library (e.g., Recharts) with strict schemas so the renderer, not the model, controls styling. Add unit tests for common visuals to prevent regressions. Visuals raise comprehension and stakeholder confidence when they’re reliable.

#### How do we match consulting-grade styling so reports don’t look AI-generated?

Define brand tokens (colors, fonts, spacing) and enforce them in templates that the model can’t override. For PowerPoint/Slides, consider a rendering pipeline where LLMs propose content, and a post‑processor applies style rules. In high‑stakes settings, a CV loop can read reviewer comments and apply exact adjustments. Expect most time to go into the final 5%—legends, markers, spacing—that signal “human‑made.” Budget for this in timelines and scope. Many buyers judge quality by polish as much as by insight.

### Domain-specific systems

#### How should we approach medical RAG with complex, timeline-heavy queries?

Split the corpus by document type (notes, labs, meds, imaging) and extract structured fields for each. Expose schema‑first tools so many questions become SQL‑like lookups, not fuzzy search. Normalize identifiers and time to align across sources. Keep free‑text for nuance and grounding but let structure answer the core facts. This reduces error rates and latency while improving auditability. Always design with privacy and on‑prem constraints in mind.

#### What’s the best way to handle temporal reasoning across clinical events?

Convert events into markdown tables with explicit timestamps, actors, and values, then sort chronologically. Models navigate these tables better than CSV/JSON for lookups and comparisons. For complex queries, do a two‑step flow: extract and align timeline rows, then reason over the aligned subset. Test both ascending and descending order because scan direction can affect accuracy. Keep units consistent and annotate gaps or missing data explicitly. This structure reduces hallucinations and speeds reasoning.

#### How do we extract and traverse structure from blueprints and other visual docs?

Use computer vision to detect rooms, labels, and orientation, then have an LLM read and normalize the labels. Extract key fields like building, floor, line, room count, and orientation into a table. Build tools to traverse by location (“floor 40, line B, 2 bedrooms, north‑facing”) like a human would. Validate extraction by sampling against human checks and fix systemic misses with small specialized models. Over time, these structures enable fast, precise retrieval and richer analytics. Invest where query logs show repeated, high‑value needs.

### Business value and pricing

#### How do we turn conversation data into systems that drive revenue, not just time savings?

Analyze conversations to find inventory gaps (“we don’t have content for X”) and missing capabilities (“we can’t filter by Y”). Prioritize small changes that drive decisions—like always attempting an upsell before ending a call. Instrument outcomes so you can prove value (conversion lift, reduced churn, higher AOV). Feed these insights back into retrieval, tooling, and prompts. Many wins don’t require heavier AI—just better process and guardrails. This is where ROI often appears first.

#### What does outcome-based pricing for AI look like in the real world?

Shift from usage fees to value fees: take a share of revenue generated, savings, or guaranteed outcomes. This forces you to measure outcomes directly and design for reliability, not just throughput. Aligning incentives changes product choices—teams invest in evaluation, guardrails, and UIs that boost trust. It also strengthens retention because customers see clear ROI. Start with hybrid models (base + success fee) while you build measurement muscle. Over time, your data makes pricing more predictable.

#### Will AI capabilities move into platforms—or remain app-level until we have the data?

In the near term, applications will own value because they collect the specific data that makes models useful. Those apps act as sensors, generating labeled interactions and edge cases. Later, platforms will absorb mature capabilities once enough cross‑app data exists. This pattern mirrors speech and vision: tools first, platforms second. If you build apps now, you earn the datasets that power tomorrow’s platform features. Don’t wait for the platform to arrive—create the data it will need.

### Guest talks: what you’ll take away

#### Single vs multi‑agent for coding (Cognition / Devin)

Why single‑agent loops often beat multi‑agent setups for code: context loss and conflicting decisions make parallel agents brittle. Read‑only sub‑agents can help, but plan‑then‑act workflows with strong context engineering are more reliable. Add cache‑aware design, integrated evals, and universal tools (shell) to boost robustness. If you use sub‑agents, pass full traces and avoid parallel edits. Expose a single coherent “agent” to users even if internals are modular.

#### Agent architecture for real work (Sourcegraph)

Agents invert retrieval: the model picks tools to fetch context instead of relying on a monolithic RAG engine. Provide a portfolio of simple tools (grep, glob, search sub‑agent, docs fetch) and couple model choice to tool design. Use sub‑agents to extend effective context for exploration without polluting the main thread. Evaluate as guardrails (like smoke tests) tied to user pain, not just recall. Keep UI minimal; focus on agent capability and feedback loops.

#### Chunking and query routing (ChromaDB, Anton)

Chunking still matters: maximize passage‑level recall while avoiding mixed, contradictory chunks. Always inspect your chunks and evaluate on your own queries. For routing, avoid the “one big index” anti‑pattern—denormalize to per‑user/per‑source indexes to improve recall and security. Route with full multiplexing + re‑rankers or with an LLM router; calibrate against data. Fine‑tune embeddings per collection where it pays.

#### Encoder stacking beyond text (Superlinked)

Complex queries mix numbers, categories, location, and text. Use a mixture of encoders and combine their vectors with weights; stop stringifying non‑text. Replace hard filters with smooth biases where possible; reduce over‑reliance on re‑ranking. Modular encoders are easier to refresh when distributions drift. Keep sparse signals around for keyword‑exact cases.

#### Search infra for AIs, not humans (Exa)

AI needs precise, context‑rich, comprehensive results; public engines optimize for a few clickable links. Embedding‑native search enables long, structured queries and bulk results. At scale, expect clustering, compression, SIMD, and “test‑time compute” for hard queries. For domain apps, hybrid lexical+dense often wins. Align incentives to quality, not ads.

#### Online monitoring and eval frameworks (Ben & Sidhant; Zapier/Vitor)

Evals are unit tests; production needs continuous signals. Track implicit (frustration, regenerations) and explicit (thumbs, success) signals; segment and prioritize with a Trellis‑style framework. Scale feedback with UX changes and “labeling parties,” then convert cases into durable evals. Use LLM‑as‑judge sparingly online due to cost/drift; prefer targeted checks. Route recurring failures to tools, prompts, or fine‑tunes.

#### Document parsing that doesn’t lie (Reducto)

Inputs gate outputs. Use hybrid CV + VLM pipelines; multi‑pass to detect, grade, and correct hard elements (tables, charts, handwriting). Choose representations per task: HTML for complex tables, Markdown for simple, image crops for figures; generate retrieval‑friendly summaries for embeddings. Build benches with 100–200 hard cases and score structure, not just text. Expect long‑tail edge cases; add confidence and fallbacks.

#### RAG anti‑patterns to avoid (Skylar)

Silent drops from encodings, tiny chunks, index staleness, vague/off‑domain queries, and re‑ranking bandaids are common failure modes. Log beyond the top‑K to catch false negatives. Break tasks down and route simple asks to fast paths. Enforce inline citations and validate spans to prevent facepalm outputs. Increase complexity only after evals prove value.

#### Generative evals for embeddings (Kelly, Chroma)

Stop over‑indexing on MTEB. Build custom evals from your docs: LLM‑judge to filter chunks users would ask about, then generate realistic queries (seeded with real examples). Compare models with recall@K on your data; expect rankings to differ from public leaderboards. Be intentional with costly contextual chunk rewriting. Keep humans in the loop to align the judge.

### Agentic RAG: beyond one‑shot retrieval

Many teams we’ve worked with (and several guest speakers) have upgraded from one‑shot “retrieve once, generate once” to agentic RAG systems that plan, retrieve, verify, and iterate. We’ll cover this deeply in office hours—how to invert context fetching so the model selects tools, how to use read‑only sub‑agents to extend effective context, and how to evaluate plans before executing. You’ll learn when to keep a single agent for coordinated edits, when to introduce sub‑agents for exploration, and how to measure P(success) across plan → tool selection → retrieval → generation. The result is higher reliability and better recall without ballooning token budgets.

## Learn more

- Read the overview: [Systematically Improving RAG](../../systematically-improving-rag-overview.md)
- Browse office hours notes: [Cohort 3](./)
