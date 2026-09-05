from langchain_core.tools import tool


@tool
def code_analyzer(code: str) -> str:
    """Analyze Python code and provide basic information about it."""

    lines = code.strip().splitlines()

    result = []

    result.append(f"Number of lines: {len(lines)}")

    if "def " in code:
        result.append("The code contains a function.")

    if "for " in code:
        result.append("The code contains a for loop.")

    if "while " in code:
        result.append("The code contains a while loop.")

    if "import " in code:
        result.append("The code contains an import statement.")

    if "print(" in code:
        result.append("The code contains a print statement.")

    return "\n".join(result)

if __name__ == "__main__":

    code = """
def greet():
    for i in range(5):
        print(i)
"""

    result = code_analyzer.invoke(code)

    print(result)