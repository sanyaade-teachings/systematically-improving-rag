```python
%load_ext autoreload
%autoreload 2
```

# Week 6 - Systematically Improving Your Rag Application

> **Prerequisites**: Make sure that you've completed the previous notebooks `1. Evaluate Tools` and `2. Generate Dataset` before continuing with this notebook. We'll be using the results from the previous notebook to evaluate the effectiveness of our new techniques.

In this notebook, we'll explore how to improve our model's ability to select the right tools using system prompts and few-shot examples.

## Why this matters

When deploying RAG systems that coordinate multiple tools, getting tool selection wrong wastes resources and degrades user experience. Simple techniques like system prompts and few-shot examples can significantly boost tool selection accuracy without complex infrastructure changes.

Just as Week 1 showed how synthetic data could improve retrieval, and Week 4 demonstrated how topic modeling helps understand query patterns, strategic prompting can help models better understand when and how to use different tools. By systematically testing these improvements against our evaluation framework, we can quantify exactly how much each change helps.

## What you'll learn

Through hands-on experimentation with a personal assistant chatbot, you'll discover how to:

1. Leverage System Prompts

- Write effective prompts that explain tool usage patterns
- Help models understand user workflows and preferences
- Validate prompt improvements with metrics

2. Design Few-Shot Examples

- Create examples that demonstrate correct tool combinations
- Target specific failure modes identified in testing
- Balance example diversity and relevance

3. Measure Improvements

- Compare performance before and after changes
- Track precision and recall across different approaches
- Make data-driven decisions about prompting strategies

By the end of this notebook, you'll understand how to systematically improve tool selection accuracy through better prompting, and how to measure the impact of these changes using objective metrics.

## System Prompts

By adding a system prompt for users to outline their specific workflow and tool usage, our model can handle a greater variety of users and their specific tool usage patterns.

Let's see this in action below where we add the user provided system prompt to our prompt template.

```python
import instructor
from helpers import load_commands, load_queries, Command, SelectedCommands

user_system_prompt = """
I work as a software engineer at a company. When it comes to work, we normally track all outstanding tasks in Jira and handle the code review/discussions in github itself.

refer to jira to get ticket information and updates but github is where code reviews, discussions and any other specific code related updates are tracked. Use the recently updated issues command to get the latest updates over search.

for todos, i use a single note in apple notes for all my todos unless i say otherwise. Obsidian is where I store diagrams, charts and notes that I've taken down for things that I'm studying up on. Our company uses confluence for documentation, wikis, release reports, meeting notes etc that need to be shared with the rest of the team. Notion I use it for financial planning, tracking expenses and planning for trips. I always use databases in notion.

For messaging apps, I tend to just use discord for chatting with my friends when we game, i use microsoft teams for communicating with colleague about spcifically work related matters and iMessage for personal day to day stuff (Eg. coordinate a party, ask about general things in a personal context)
"""


async def generate_commands_with_system_prompt(
    query: str,
    client: instructor.AsyncInstructor,
    commands: list[Command],
    user_system_prompt: str,
):
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
                You are a helpful assistant that can execute commands in response to a user query. You have access to the following commands:

                <commands>
                {% for command in commands %}
                - {{ command.key }} : {{ command.command_description }}
                {% endfor %}
                </commands>

                You must select at least one command to be called.

                Here is some information about how the user uses each extension. Remember to find a chat before sending a message.

                <user_behaviour>
                {{ user_behaviour }}
                </user_behaviour>
                """,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        model="gpt-4o",
        response_model=SelectedCommands,
        context={"commands": commands, "user_behaviour": user_system_prompt},
    )
    return response.selected_commands
```

    /Users/ivanleo/Documents/coding/systematically-improving-rag/cohort_2/.venv/lib/python3.9/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
      warnings.warn(

Let's now run our evaluations again to see how it performs.

```python
import instructor
from openai import AsyncOpenAI

commands = load_commands("raw_commands.json")
queries = load_queries(commands, "queries.jsonl")
client = instructor.from_openai(AsyncOpenAI())
await generate_commands_with_system_prompt(
    "notify #engineering that I'm running late for our meeting and i'll be there in 20 minutes",
    client,
    commands,
    user_system_prompt,
)
```

    [UserCommand(key='microsoft-teams.findChat', arguments=[UserCommandArgument(title='Chat or Channel Name', value='#engineering')])]

```python
from braintrust import Score, EvalAsync
from helpers import calculate_precision, calculate_recall


def evaluate_braintrust(input, output, **kwargs):
    return [
        Score(
            name="precision",
            score=calculate_precision(output, kwargs["expected"]),
        ),
        Score(
            name="recall",
            score=calculate_recall(output, kwargs["expected"]),
        ),
    ]


commands = load_commands("raw_commands.json")
queries = load_queries(commands, "queries.jsonl")


client = instructor.from_openai(AsyncOpenAI())
commands = load_commands("raw_commands.json")
queries = load_queries(commands, "queries.jsonl")


async def task(query, hooks):
    resp = await generate_commands_with_system_prompt(
        query, client, commands, user_system_prompt
    )
    hooks.meta(
        input=query,
        output=resp,
    )
    return [item.key for item in resp]


results = await EvalAsync(
    "function-calling",
    data=[
        {
            "input": row["query"],
            "expected": row["labels"],
        }
        for row in queries
    ],
    task=task,
    scores=[evaluate_braintrust],
)
```

    Experiment week-6-fixes-1741091518 is running at https://www.braintrust.dev/app/567/p/function-calling/experiments/week-6-fixes-1741091518
    function-calling (data): 51it [00:00, 63268.12it/s]



    function-calling (tasks):   0%|          | 0/51 [00:00<?, ?it/s]


    /var/folders/ws/q_m6c6qs3n553603dk_zvrgc0000gn/T/ipykernel_48785/1736270016.py:31: DeprecationWarning: meta() is deprecated. Use the metadata field directly instead.
      hooks.meta(



    =========================SUMMARY=========================
    week-6-fixes-1741091518 compared to week-6-fixes-1741091506:
    54.25% (+00.47%) 'recall'    score	(5 improvements, 5 regressions)
    63.55% (+03.10%) 'precision' score	(8 improvements, 8 regressions)

    1741091518.79s start
    1741091521.06s end
    2.27s (+14.47%) 'duration'	(24 improvements, 27 regressions)

    See results for week-6-fixes-1741091518 at https://www.braintrust.dev/app/567/p/function-calling/experiments/week-6-fixes-1741091518

Performance Improvement with System Prompt

| Metric    | Baseline | System Prompt |
| --------- | -------- | ------------- |
| Precision | 0.45     | 0.64 (+42%)   |
| Recall    | 0.40     | 0.54 (+35%)   |

By providing a system prompt, we saw a significant improvement in performance across both precision and recall metrics.

This is a significant improvement and shows that providing a system prompt can help the model understand how the user uses each tool.

Better yet, using system prompts allow our model to be more flexible and handle a greater variety of users that may have different ways of interacting with the tools.

### Comparing System Prompts with Baseline

Now that we've seen a overall improvement across the board, let's look at what specific queries our model is having issues with. Let's do so by computing the same metrics as we did in our previous notebook

```python
import pandas as pd
from helpers import (
    calculate_per_tool_recall,
    calculate_precision_recall_for_queries,
    get_mismatched_examples_for_tool,
)

df = pd.DataFrame(
    [
        {
            "query": row.input,
            "expected": row.expected,
            "actual": row.output,
        }
        for row in results.results
    ]
)

df = calculate_precision_recall_for_queries(df)
df.head(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>expected</th>
      <th>actual</th>
      <th>precision</th>
      <th>recall</th>
      <th>CORRECT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>create a grocery list note with Milk, eggs, br...</td>
      <td>[apple-notes.new, apple-notes.add-text, apple-...</td>
      <td>[apple-notes.new, apple-notes.menu-bar, apple-...</td>
      <td>0.67</td>
      <td>0.67</td>
      <td>N</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Let's create a new release post about our late...</td>
      <td>[confluence-search.new-blog, jira.active-sprin...</td>
      <td>[jira.recently-updated-issues, confluence-sear...</td>
      <td>0.50</td>
      <td>0.25</td>
      <td>N</td>
    </tr>
    <tr>
      <th>2</th>
      <td>find weather taiwan december and generate a sh...</td>
      <td>[google-search.index, apple-notes.new, apple-n...</td>
      <td>[google-search.index, apple-notes.index]</td>
      <td>0.50</td>
      <td>0.33</td>
      <td>N</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Set my status to 'Working from home today, cat...</td>
      <td>[microsoft-teams.setStatus]</td>
      <td>[microsoft-teams.setStatus, microsoft-teams.fi...</td>
      <td>0.33</td>
      <td>1.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>4</th>
      <td>any security alerts raised since we upgraded o...</td>
      <td>[github.unread-notifications]</td>
      <td>[github.search-issues]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Tell mum i'll be back for dinner around 7pm</td>
      <td>[imessage.findChat, imessage.sendMessage]</td>
      <td>[imessage.findChat]</td>
      <td>1.00</td>
      <td>0.50</td>
      <td>N</td>
    </tr>
    <tr>
      <th>6</th>
      <td>just booked the latest accomodations for tokyo...</td>
      <td>[notion.create-database-page]</td>
      <td>[notion.create-database-page]</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>7</th>
      <td>search messages Gregory modal, need to find th...</td>
      <td>[microsoft-teams.searchMessages]</td>
      <td>[microsoft-teams.findChat]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>8</th>
      <td>add a reminder to my todos to buy some groceri...</td>
      <td>[apple-notes.add-text]</td>
      <td>[apple-notes.add-text]</td>
      <td>1.00</td>
      <td>1.00</td>
      <td>Y</td>
    </tr>
    <tr>
      <th>9</th>
      <td>pull up munich plans, send mike the airbnb lin...</td>
      <td>[notion.search-page, imessage.findChat, imessa...</td>
      <td>[notion.search-page, imessage.findChat]</td>
      <td>1.00</td>
      <td>0.67</td>
      <td>N</td>
    </tr>
  </tbody>
</table>
</div>

```python
df_per_tool = calculate_per_tool_recall(df)
df_per_tool.sort_values(by="recall", ascending=True).head(20)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tool</th>
      <th>actual</th>
      <th>expected</th>
      <th>recall</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>21</th>
      <td>jira.open-issues</td>
      <td>0</td>
      <td>1</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>2</th>
      <td>confluence-search.add-text</td>
      <td>0</td>
      <td>1</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>27</th>
      <td>jira.active-sprints</td>
      <td>0</td>
      <td>2</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>30</th>
      <td>microsoft-teams.searchMessages</td>
      <td>0</td>
      <td>1</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>16</th>
      <td>discord.sendMessage</td>
      <td>0</td>
      <td>3</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>6</th>
      <td>github.my-pull-requests</td>
      <td>0</td>
      <td>2</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>15</th>
      <td>microsoft-teams.sendMessage</td>
      <td>0</td>
      <td>13</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>8</th>
      <td>imessage.sendMessage</td>
      <td>0</td>
      <td>5</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>14</th>
      <td>discord.searchMessages</td>
      <td>0</td>
      <td>1</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>24</th>
      <td>confluence-search.go</td>
      <td>0</td>
      <td>1</td>
      <td>0.00</td>
    </tr>
    <tr>
      <th>31</th>
      <td>github.unread-notifications</td>
      <td>1</td>
      <td>5</td>
      <td>0.20</td>
    </tr>
    <tr>
      <th>13</th>
      <td>confluence-search.search</td>
      <td>1</td>
      <td>3</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>25</th>
      <td>jira.search-issues</td>
      <td>1</td>
      <td>3</td>
      <td>0.33</td>
    </tr>
    <tr>
      <th>29</th>
      <td>confluence-search.new-blog</td>
      <td>1</td>
      <td>2</td>
      <td>0.50</td>
    </tr>
    <tr>
      <th>28</th>
      <td>apple-notes.new</td>
      <td>1</td>
      <td>2</td>
      <td>0.50</td>
    </tr>
    <tr>
      <th>20</th>
      <td>obsidian.searchMedia</td>
      <td>2</td>
      <td>3</td>
      <td>0.67</td>
    </tr>
    <tr>
      <th>23</th>
      <td>apple-notes.add-text</td>
      <td>5</td>
      <td>7</td>
      <td>0.71</td>
    </tr>
    <tr>
      <th>10</th>
      <td>microsoft-teams.findChat</td>
      <td>10</td>
      <td>13</td>
      <td>0.77</td>
    </tr>
    <tr>
      <th>33</th>
      <td>microsoft-teams.unreadMessages</td>
      <td>1</td>
      <td>1</td>
      <td>1.00</td>
    </tr>
    <tr>
      <th>34</th>
      <td>notion.search-page</td>
      <td>1</td>
      <td>1</td>
      <td>1.00</td>
    </tr>
  </tbody>
</table>
</div>

From the table above, we can see that some potential function calls with a high discrepancy between the expected calls and actual calls are

1. `microsoftTeams.sendMessage` and `imessage.sendMessage`
2. `github.unreadNotifications`
3. `discord.findChat` and `discord.sendMessage`

We'll grab some of these examples where a specific tool call didn't get executed below

```python
# Set display width to maximum
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", None)

# Example usage for unread-notifications
unread_notification_examples = get_mismatched_examples_for_tool(
    df, "unread-notifications", num_examples=5
)
unread_notification_examples
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>expected</th>
      <th>actual</th>
      <th>precision</th>
      <th>recall</th>
      <th>CORRECT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>any security alerts raised since we upgraded our nextjs dependencies over to 14.2.0?</td>
      <td>[github.unread-notifications]</td>
      <td>[github.search-issues]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>22</th>
      <td>any more prs or security alerts to worry about?</td>
      <td>[github.unread-notifications]</td>
      <td>[github.my-pull-requests, github.notifications, github.unread-notifications]</td>
      <td>0.33</td>
      <td>1.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>48</th>
      <td>check if there are any dependency vulnerabilities raised recently</td>
      <td>[github.unread-notifications]</td>
      <td>[jira.recently-updated-issues, github.notifications, github.search-issues]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>49</th>
      <td>did anyone comment on the pr for the performance fix?</td>
      <td>[github.unread-notifications]</td>
      <td>[github.my-pull-requests]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>50</th>
      <td>pull up those security alerts and ping the security team</td>
      <td>[github.unread-notifications, microsoft-teams.findChat, microsoft-teams.sendMessage]</td>
      <td>[github.notifications, microsoft-teams.findChat]</td>
      <td>0.50</td>
      <td>0.33</td>
      <td>N</td>
    </tr>
  </tbody>
</table>
</div>

```python
unread_notification_examples = get_mismatched_examples_for_tool(
    df, "unread-notifications", num_examples=5
)
unread_notification_examples
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>expected</th>
      <th>actual</th>
      <th>precision</th>
      <th>recall</th>
      <th>CORRECT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>4</th>
      <td>any security alerts raised since we upgraded our nextjs dependencies over to 14.2.0?</td>
      <td>[github.unread-notifications]</td>
      <td>[github.search-issues]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>22</th>
      <td>any more prs or security alerts to worry about?</td>
      <td>[github.unread-notifications]</td>
      <td>[github.my-pull-requests, github.notifications, github.unread-notifications]</td>
      <td>0.33</td>
      <td>1.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>48</th>
      <td>check if there are any dependency vulnerabilities raised recently</td>
      <td>[github.unread-notifications]</td>
      <td>[jira.recently-updated-issues, github.notifications, github.search-issues]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>49</th>
      <td>did anyone comment on the pr for the performance fix?</td>
      <td>[github.unread-notifications]</td>
      <td>[github.my-pull-requests]</td>
      <td>0.00</td>
      <td>0.00</td>
      <td>N</td>
    </tr>
    <tr>
      <th>50</th>
      <td>pull up those security alerts and ping the security team</td>
      <td>[github.unread-notifications, microsoft-teams.findChat, microsoft-teams.sendMessage]</td>
      <td>[github.notifications, microsoft-teams.findChat]</td>
      <td>0.50</td>
      <td>0.33</td>
      <td>N</td>
    </tr>
  </tbody>
</table>
</div>

```python
send_message_examples = get_mismatched_examples_for_tool(
    df, "imessage.sendMessage", num_examples=5
)
send_message_examples
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>expected</th>
      <th>actual</th>
      <th>precision</th>
      <th>recall</th>
      <th>CORRECT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>5</th>
      <td>Tell mum i'll be back for dinner around 7pm</td>
      <td>[imessage.findChat, imessage.sendMessage]</td>
      <td>[imessage.findChat]</td>
      <td>1.0</td>
      <td>0.50</td>
      <td>N</td>
    </tr>
    <tr>
      <th>9</th>
      <td>pull up munich plans, send mike the airbnb link to the accoms on the 22nd</td>
      <td>[notion.search-page, imessage.findChat, imessage.sendMessage]</td>
      <td>[notion.search-page, imessage.findChat]</td>
      <td>1.0</td>
      <td>0.67</td>
      <td>N</td>
    </tr>
    <tr>
      <th>27</th>
      <td>Message David to ask if he's still up for basketball this weekend</td>
      <td>[imessage.findChat, imessage.sendMessage]</td>
      <td>[imessage.findChat]</td>
      <td>1.0</td>
      <td>0.50</td>
      <td>N</td>
    </tr>
    <tr>
      <th>28</th>
      <td>Send Kevin a message asking if he still has my charger</td>
      <td>[imessage.findChat, imessage.sendMessage]</td>
      <td>[imessage.findChat]</td>
      <td>1.0</td>
      <td>0.50</td>
      <td>N</td>
    </tr>
    <tr>
      <th>29</th>
      <td>Tell Alex I'm running 15 minutes late for brunch</td>
      <td>[imessage.findChat, imessage.sendMessage]</td>
      <td>[imessage.findChat]</td>
      <td>1.0</td>
      <td>0.50</td>
      <td>N</td>
    </tr>
  </tbody>
</table>
</div>

```python
send_message_examples = get_mismatched_examples_for_tool(
    df, "discord.sendMessage", num_examples=5
)
send_message_examples
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }

</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>expected</th>
      <th>actual</th>
      <th>precision</th>
      <th>recall</th>
      <th>CORRECT</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>12</th>
      <td>let's go crack open that new raid, set status to dnd and ping #bois</td>
      <td>[discord.setStatus, discord.findChat, discord.sendMessage]</td>
      <td>[discord.setStatus, discord.findChat]</td>
      <td>1.0</td>
      <td>0.67</td>
      <td>N</td>
    </tr>
    <tr>
      <th>44</th>
      <td>tell #team-alpha I'll be late for tonight's dungeon run</td>
      <td>[discord.findChat, discord.sendMessage]</td>
      <td>[discord.findChat]</td>
      <td>1.0</td>
      <td>0.50</td>
      <td>N</td>
    </tr>
    <tr>
      <th>45</th>
      <td>drop a message in #guild chat that I'm taking a break and set status to idle for now</td>
      <td>[discord.setStatus, discord.findChat, discord.sendMessage]</td>
      <td>[discord.findChat, discord.setStatus]</td>
      <td>1.0</td>
      <td>0.67</td>
      <td>N</td>
    </tr>
  </tbody>
</table>
</div>

### Few Shot Prompting

Once we've identified potential problem areas - like the model failing to find findChat - few shot examples can explicitly demonstrate these commands used in context.

For instance, we can show a few examples of how to use the `findChat` command with a `sendMessage` command. A natural fit here could be to grab some content from an internal documentation site like `confluence` and then sending it over to a chat.

```
<query>generate release notes for the tickets closed in our current sprint and send the link over to the #product channel ahead of time so they know what's coming</query>
<commands>
    confluence-search.new-blog,
    confluence-search.add-text,
    microsoft-teams.findChat,
    microsoft-teams.sendMessage
</commands>
```

We could also be inventive and use the `searchMedia` command alongside a normal `searchNoteCommand` to show the model how each command differs.

```
<query>Can you grab my notes and sketches which I put together about cross-attention?</query>
<commands>
    obsidian.searchMedia,
    obsidian.searchNote
</commands>
```

Including these concrete examples in the prompt teaches the model the correct sequence of steps and drastically reduces the chances it calls the wrong command.”

```python
async def generate_commands_with_prompt_and_examples(
    query: str,
    client: instructor.AsyncInstructor,
    commands: list[Command],
    user_behaviour: str,
):
    response = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": """
You are a helpful assistant that can execute commands in response to a user query. Only choose from the commands listed below.

You have access to the following commands:

<commands>
{% for command in commands %}
<command>
    <command key>{{ command.key }}</command key>
    <command description>{{ command.command_description }}</command description>
</command>
{% endfor %}
</commands>

Select between 1-4 commands to be called in response to the user query.

Here is some information about how the user uses each extension. Remember to find a chat before sending a message.

<user_behaviour>
{{ user_behaviour }}
</user_behaviour>

Here are some past examples of queries that the user has asked in the past and the keys of the commands that were expected to be called. These provide valuable context and so look at it carefully and understand why each command was called, taking into account the user query below and the user behaviour provided above.

<examples>
    <example>
        <query>Compile any new outstanding PRs that have been reviewed recently with any vulnerabilities that have been reported and send them in a message to the engineering team in the #engineering channel to fix it before our next release</query>
        <commands>
            github.unread-notifications
            microsoft-teams.findChat
            microsoft-teams.sendMessage
        </commands>
    </example>
    <example>
        <query>Can you text Philip a link to the notion document for our trip to Taiwan next week?</query>
        <commands>
            notion.search
            imessage.findChat
            imessage.sendMessage
        </commands>
    </example>
    <example>
        <query>Can you pull up the visualisation I made to show how our D&D dungeon map layout works and then forward it to the party members in #gaming?</query>
        <commands>
            obsidian.searchMedia
            discord.findChat
            discord.sendMessage
        </commands>
    </example>
</examples>
                """,
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        model="gpt-4o",
        response_model=SelectedCommands,
        context={"commands": commands, "user_behaviour": user_behaviour},
    )
    return response.selected_commands
```

```python
def evaluate_braintrust(input, output, **kwargs):
    return [
        Score(
            name="precision",
            score=calculate_precision(output, kwargs["expected"]),
        ),
        Score(
            name="recall",
            score=calculate_recall(output, kwargs["expected"]),
        ),
    ]


commands = load_commands("raw_commands.json")
queries = load_queries(commands, "queries.jsonl")


client = instructor.from_openai(AsyncOpenAI())
commands = load_commands("raw_commands.json")
queries = load_queries(commands, "queries.jsonl")


async def task(query, hooks):
    resp = await generate_commands_with_prompt_and_examples(
        query, client, commands, user_system_prompt
    )
    hooks.meta(
        input=query,
        output=resp,
    )
    return [item.key for item in resp]


results = await EvalAsync(
    "function-calling",
    data=[
        {
            "input": row["query"],
            "expected": row["labels"],
        }
        for row in queries
    ],
    task=task,
    scores=[evaluate_braintrust],
)
```

    Experiment week-6-fixes-1741092345 is running at https://www.braintrust.dev/app/567/p/function-calling/experiments/week-6-fixes-1741092345
    function-calling (data): 51it [00:00, 47940.27it/s]



    function-calling (tasks):   0%|          | 0/51 [00:00<?, ?it/s]


    /var/folders/ws/q_m6c6qs3n553603dk_zvrgc0000gn/T/ipykernel_48785/4256564407.py:27: DeprecationWarning: meta() is deprecated. Use the metadata field directly instead.
      hooks.meta(



    =========================SUMMARY=========================
    week-6-fixes-1741092345 compared to week-6-fixes-1741092333:
    78.94% (+05.75%) 'recall'    score	(9 improvements, 7 regressions)
    83.96% (+08.14%) 'precision' score	(10 improvements, 7 regressions)

    1741092344.94s start
    1741092347.20s end
    2.26s (-03.44%) 'duration'	(28 improvements, 23 regressions)

    See results for week-6-fixes-1741092345 at https://www.braintrust.dev/app/567/p/function-calling/experiments/week-6-fixes-1741092345

## Conclusion

In this notebook, we've shown how simple techniques like few-shot prompting and system prompts can significantly boost model performance in tool selection.

| Metric    | Baseline | System Prompt | System Prompt + Few Shot |
| --------- | -------- | ------------- | ------------------------ |
| Precision | 0.45     | 0.64 (+42%)   | 0.79 (+76%)              |
| Recall    | 0.40     | 0.54 (+35%)   | 0.84 (+110%)             |

These gains came from two key insights : clear system prompts help models understand tool usage patterns (like using Teams for work vs Discord for gaming), while targeted examples prevent common mistakes like forgetting to find a chat before sending a message.

This reflects the systematic pattern we've followed throughout the course. Each week started by defining clear metrics to optimize - whether that was MRR and recall for retrieval (Week 1), recall and MRR for metadata filtering in Week 5, or precision metrics for tool selection here in Week 6. With these metrics in place, we could use synthetic data to rapidly test improvements and validate the improvements that our changes have on the system.

As we deploy these systems to production, this data-driven approach becomes even more crucial. By collecting real user feedback through UI elements like thumbs up/down ratings and establishing clear evaluation metrics early, teams can quantify the impact of each change they make. This systematic strategy - defining metrics, using synthetic data for rapid testing, then validating with real user feedback - provides a reliable framework for improving RAG systems even as they grow more complex with multiple data sources, tools and retrieval methods.

---

--8<--
  "snippets/enrollment-button.md"
--8<--

---


---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
