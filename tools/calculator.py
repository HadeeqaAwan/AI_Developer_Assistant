from langchain_core.tools import tool


@tool
def calculator(expression: str) -> str:
    """Calculate a mathematical expression."""

    print(f">>> Calculator Tool called with: {expression}")

    try:
        result = eval(expression, {"__builtins__": {}}, {})
        print(f">>> Calculator Result: {result}")
        return str(result)

    except Exception as e:
        print(f">>> Calculator Error: {e}")
        return f"Error: {e}"


if __name__ == "__main__":
    result = calculator.invoke("25 * 48")
    print(result)