import streamlit as st
import json
import pandas as pd
from const import gl_codes, departments


def load_transactions():
    transactions = []
    try:
        with open("transactions.jsonl", "r") as f:
            for line in f:
                transactions.append(json.loads(line))
        return pd.DataFrame(transactions)
    except FileNotFoundError:
        st.error("transactions.jsonl file not found")
        return pd.DataFrame()


def save_transaction(transaction):
    with open("generated.jsonl", "a") as f:
        f.write(json.dumps(transaction) + "\n")


def main():
    st.title("Transaction Annotation Queue")

    # Initialize session state for tracking reviewed transactions
    if "reviewed_indices" not in st.session_state:
        st.session_state.reviewed_indices = set()

    # Load data
    df = load_transactions()

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
    st.sidebar.header("Transaction Queue")

    # Get transaction IDs or another unique identifier to select from
    selected_index = st.sidebar.selectbox(
        "Select Transaction to Review",
        remaining_indices,
        format_func=lambda x: f"Transaction {x + 1}",
    )

    # Display selected transaction
    # st.header(f"Transaction {selected_index + 1} Review")

    # Get the selected transaction
    selected_transaction = df.iloc[selected_index]

    # Display transaction details in text fields with editing enabled
    edited_transaction = {}
    edited_transaction["transaction_name"] = st.text_input(
        "Transaction Name", selected_transaction["transaction_name"]
    )
    edited_transaction["amount"] = st.text_input(
        "Amount", selected_transaction["amount"]
    )
    edited_transaction["location"] = st.text_input(
        "Location", selected_transaction["location"]
    )
    edited_transaction["department"] = st.selectbox(
        "Department",
        options=departments,
        index=departments.index(selected_transaction["department"]),
    )
    edited_transaction["category"] = st.selectbox(
        "Category",
        options=[code["name"] for code in gl_codes],
        index=[code["name"] for code in gl_codes].index(
            selected_transaction["category"]
        )
        if selected_transaction["category"] in [code["name"] for code in gl_codes]
        else 0,
    )

    # Add approve/reject buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Approve"):
            save_transaction(edited_transaction)  # Save the edited version instead
            st.session_state.reviewed_indices.add(selected_index)  # Mark as reviewed
            st.success("Transaction approved and saved!")
            st.rerun()  # Rerun to update the interface

    with col2:
        if st.button("❌ Skip"):
            st.session_state.reviewed_indices.add(selected_index)  # Mark as reviewed
            st.info("Moving to next transaction...")
            st.rerun()

    # Show progress in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Review Progress")
    st.sidebar.write(f"Remaining to Review: {len(remaining_indices)}")


if __name__ == "__main__":
    main()
