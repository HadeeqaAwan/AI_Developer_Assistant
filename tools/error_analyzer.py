from langchain_core.tools import tool


@tool
def error_analyzer(error: str) -> str:
    """Analyze a Python error message and provide a simple explanation."""

    error_lower = error.lower()

    if "nameerror" in error_lower:
        return (
            "NameError: Python cannot find the variable or function name. "
            "Check whether it is defined or spelled correctly."
        )

    if "typeerror" in error_lower:
        return (
            "TypeError: An operation or function was used with an incompatible type. "
            "Check the data types of the values."
        )

    if "syntaxerror" in error_lower:
        return (
            "SyntaxError: Python found invalid syntax. "
            "Check brackets, colons, indentation, and spelling."
        )

    if "indexerror" in error_lower:
        return (
            "IndexError: You tried to access a list or sequence position "
            "that does not exist."
        )

    if "keyerror" in error_lower:
        return (
            "KeyError: The requested key does not exist in the dictionary."
        )

    if "attributeerror" in error_lower:
        return (
            "AttributeError: The object does not have the attribute or method "
            "you are trying to use."
        )

    return (
        "The error type was not recognized. "
        "Check the traceback and the line where the error occurred."
    )


if __name__ == "__main__":

    test_error = "NameError: name 'username' is not defined"

    result = error_analyzer.invoke(test_error)

    print(result)