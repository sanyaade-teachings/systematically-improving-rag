# Introduction

This is a project that demonstrates why and how we need to do segmentation in the first place when dealing with user queries. We'll be using a synthetic dataset of user queries and corresponding labels to show how we can use segmentation to improve the performance of our model.

We'll generate a synthetic dataset of user queries and corresponding labels to show why segmentation is important. We'll have three notebooks in this project

1. `01_generate_dataset.ipynb`: Generates a synthetic dataset of user queries with underlying labels. We've provided a complete dataset in the repo but you can also take a stab at generating your own if you'd like to with new categories.
2. `02_train_model.ipynb`: We'll then show how we can use a .yaml file to label and identify query types. We'll then label each query to identify inventory or capability issues.
3. `03_label_model.ipynb`: Finally, we'll use BERTopic to train a topic model, see what topics might emerge from these user queries and then see how closely these topics aligned with our original labels.

## Installation Instructions

1. To start, first install all the required dependencies

```bash
uv pip install -r pyproject.toml
```
