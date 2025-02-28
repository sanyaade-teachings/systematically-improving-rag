import streamlit as st
import json
import pandas as pd
from streamlit_shortcuts import button
from pydantic import BaseModel
import os


class Question(BaseModel):
    question: str
    answer: str
    category: str
    citations: list[str]
    subcategory: str
    sources: list[str]


def load_questions():
    questions = []
    try:
        with open("./data/synthetic_questions.jsonl", "r") as f:
            for line in f:
                questions.append(json.loads(line))
        return pd.DataFrame(questions)
    except FileNotFoundError:
        st.error("synthetic_questions.jsonl file not found")
        return pd.DataFrame()


def save_question(question):
    with open("./data/cleaned.jsonl", "a") as f:
        f.write(Question(**question).model_dump_json() + "\n")


def load_source_content(source_path):
    path = os.path.join(os.getcwd(), "data", "md", f"{source_path}.md")
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Source file {path} not found"


def main():
    # Make the page layout wider
    st.set_page_config(layout="wide")

    st.title("Transaction Annotation Queue")

    # Initialize session state for tracking reviewed transactions
    if "reviewed_indices" not in st.session_state:
        st.session_state.reviewed_indices = set()

    # Load data
    df = load_questions()

    if df.empty:
        st.write("No transactions to review")
        return

    # Filter out reviewed transactions
    remaining_indices = [
        i for i in range(len(df)) if i not in st.session_state.reviewed_indices
    ]

    if not remaining_indices:
        st.write("All transactions have been reviewed!")
        return

    # Sidebar selection
    st.sidebar.header("Question Queue")

    selected_index = st.sidebar.selectbox(
        "Select Question to Review",
        remaining_indices,
        format_func=lambda x: f"Question {x + 1}",
    )

    # Get the selected question
    selected_question = df.iloc[selected_index]

    # Adding custom CSS to make the right column scrollable
    st.markdown(
        """
    <style>
    /* Make the right column scrollable */
    [data-testid="column"]:nth-of-type(2) {
        height: 80vh;
        overflow-y: auto !important;
    }
    
    /* Remove extra spacing */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Create a two-column layout
    left_col, right_col = st.columns([1, 1])

    # Left column: Question details and editing
    with left_col:
        st.subheader("Question Details")

        # Create text fields for editing
        edited_question = selected_question.copy()
        edited_question["question"] = st.text_area(
            "Edit Question", value=selected_question["question"], height=150
        )

        st.write(f"**Answer:** {selected_question['answer']}")
        st.write(f"**Category:** {selected_question['category']}")
        st.write(f"**Subcategory:** {selected_question['subcategory']}")

        # Add a button to copy text to clipboard
        if st.button("Generate Prompt with Context", key="copy_button"):
            items = [load_source_content(slug) for slug in selected_question["sources"]]
            context = "\n-".join(items)
            # Build the prompt text
            prompt_text = f"""
Generate 5 diverse variations of this specific question given below that users might send.

<question>
{selected_question["question"]}
</question>

For each generated message:
- Keep messages concise (1-2 sentences at most)
- Vary the product being mentioned in at least one example
- Change the location or invent one (e.g., if context mentions Canada, create a query from someone in Japan)
- Use different emotional tones (frustrated, confused, urgent, polite, desperate, annoyed, etc.)
- Create distinct customer personas (tech novice, first-time user, frequent shopper, elderly customer, etc.)
- Focus on different Klarna-related problems (payment issues, app problems, purchase questions, etc.)
- Use different portions of the context or add specific details a user might include (payment method, store they bought from, etc.)
- Look closely at examples for inspiration but don't copy them exactly

Remember that customers care about their shopping experience, not technical details. They'll describe issues from their perspective as shoppers (e.g., "my payment won't go through" rather than "the API is failing").

For each message, consider:
1. What specific problem is this customer facing?
2. What outcome do they want from contacting support?
3. How is their situation and communication style unique from the other examples?


<context>
{context}
</context>

Remember to think carefully about the context, reason through the potential questions, understand the customer's context and motivations.
"""

            # Create a download link for the file

            # Also display the text for easy copy-paste
            st.text_area("Copy a prompt from here", prompt_text, height=200)

        # Add approve/reject buttons at the bottom of the left column
        col1, col2 = st.columns(2)
        with col1:
            if button(
                "✅ Approve",
                "ctrl+e",
                on_click=lambda: st.success("Transaction approved and saved!"),
            ):
                save_question(edited_question)
                st.session_state.reviewed_indices.add(selected_index)
                st.rerun()

        with col2:
            if button(
                "❌ Skip",
                "ctrl+r",
                on_click=lambda: st.info("Moving to next transaction..."),
            ):
                st.session_state.reviewed_indices.add(selected_index)
                st.rerun()

    # Right column with citations and sources
    with right_col:
        # Citations section
        st.subheader("Citations")
        for i, citation in enumerate(selected_question["citations"]):
            st.write(f"- {citation}")

        st.markdown("---")

        # Sources section
        st.subheader("Sources")
        for source in selected_question["sources"]:
            with st.expander(f"Source: {source}"):
                source_content = load_source_content(source)
                st.markdown(source_content)

    # Show progress in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Review Progress")
    st.sidebar.write(f"Remaining to Review: {len(remaining_indices)}")
    st.sidebar.write("""
    We've provided hotkeys for you to use in this case

    1. ctrl + e to approve
    2. ctrl + r to reject
                     
    All of the approved transactions will be saved to `cleaned.jsonl` and we'll use these to generate a new set of transactions that are more challenging.
    """)


if __name__ == "__main__":
    main()
