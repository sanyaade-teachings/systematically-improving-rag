def calculate_precision(model_tool_call, expected_tool_call):
    """
    Calculate precision: (true positives) / (true positives + false positives)
    Precision = (relevant tools called) / (total tools called)
    """
    if len(model_tool_call) == 0:
        return 0.0  # Changed from 1 since no tools called means no true positives

    relevant_results = sum(1 for tool in model_tool_call if tool in expected_tool_call)
    return round(relevant_results / len(model_tool_call), 2)


def calculate_recall(model_tool_call, expected_tool_call):
    """
    Calculate recall: (true positives) / (true positives + false negatives)
    Recall = (relevant tools called) / (total relevant tools)
    """
    if len(expected_tool_call) == 0:
        return 1.0  # Perfect recall if no tools were expected

    if len(model_tool_call) == 0:
        return 0.0  # No recall if no tools were called

    relevant_results = sum(1 for tool in expected_tool_call if tool in model_tool_call)
    return round(relevant_results / len(expected_tool_call), 2)
