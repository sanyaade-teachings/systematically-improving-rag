The files in this directory create a fine-tuned reranking model on cohere and then test recall on this fine-tuned model.

You can compare it to the [results from week 1](https://github.com/567-labs/systematically-improving-rag/blob/main/week1_bootstrap_evals/metrics.ipynb) where we used a cohere reranker that had not been fine-tuned.

The key files in this directory are:

- `finetune_sbert.py`: Fine tune a sentence transformer cross-encoder. Run this before `eval_sbert.py`.
- `eval_sbert.py`: Evaluate recall for both the base sentence transformer model and the fine-tuned model
- `cohere_fine_tuning.ipynb`: Create a fine-tuned cohere model and test precision/recall

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
