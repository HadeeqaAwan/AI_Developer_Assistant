import streamlit as st
from langchain_core.messages import HumanMessage

from multi_agent import app as agent_app


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Developer Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("AI Developer Assistant")

    st.caption(
        "Multi-agent development assistant powered by "
        "LangGraph and Gemini."
    )

    st.divider()

    if st.button(
        "Clear Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.subheader("Agents")

    st.markdown("**Supervisor**")
    st.caption(
        "Routes requests to the appropriate agent."
    )

    st.markdown("**Coding Agent**")
    st.caption(
        "Handles coding, calculations and code analysis."
    )

    st.markdown("**Debug Agent**")
    st.caption(
        "Diagnoses programming errors and debugging issues."
    )

    st.markdown("**Research Agent**")
    st.caption(
        "Explains technical concepts and development topics."
    )

    st.divider()

    st.subheader("Available Tools")

    st.markdown("**Calculator**")
    st.caption(
        "Mathematical expression evaluation."
    )

    st.markdown("**Code Analyzer**")
    st.caption(
        "Python code analysis."
    )

    st.markdown("**Error Analyzer**")
    st.caption(
        "Python error diagnosis."
    )

    st.markdown("**Tech Info**")
    st.caption(
        "Technical information lookup."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("AI Developer Assistant")

st.caption(
    "Intelligent multi-agent assistant for coding, "
    "debugging, research and developer productivity."
)


# ============================================================
# WELCOME MESSAGE
# ============================================================

if not st.session_state.messages:

    st.info(
        "Ask a coding question, analyze a Python error, "
        "calculate an expression, review code, or learn "
        "about a technical concept."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a coding, debugging, or technical question..."
)


# ============================================================
# PROCESS USER MESSAGE
# ============================================================

if user_input:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)


    # --------------------------------------------------------
    # Generate assistant response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Processing your request..."):

            try:

                result = agent_app.invoke(
                    {
                        "messages": [
                            HumanMessage(
                                content=user_input
                            )
                        ]
                    }
                )


                # ------------------------------------------------
                # Extract final response
                # ------------------------------------------------

                final_response = ""

                for message in reversed(
                    result.get("messages", [])
                ):

                    if not hasattr(message, "content"):
                        continue

                    content = message.content

                    if not content:
                        continue


                    # --------------------------------------------
                    # Gemini sometimes returns a list
                    # --------------------------------------------

                    if isinstance(content, list):

                        text_parts = []

                        for item in content:

                            if isinstance(item, dict):

                                if item.get("type") == "text":

                                    text_parts.append(
                                        item.get("text", "")
                                    )

                                elif "text" in item:

                                    text_parts.append(
                                        item["text"]
                                    )

                            elif isinstance(item, str):

                                text_parts.append(item)


                        final_response = "\n".join(
                            text_parts
                        ).strip()


                    # --------------------------------------------
                    # Normal string response
                    # --------------------------------------------

                    elif isinstance(content, str):

                        final_response = content.strip()


                    # --------------------------------------------
                    # Other response types
                    # --------------------------------------------

                    else:

                        final_response = str(content).strip()


                    if final_response:
                        break


                # ------------------------------------------------
                # Fallback
                # ------------------------------------------------

                if not final_response:

                    final_response = (
                        "I was unable to generate a response."
                    )


                # ------------------------------------------------
                # Display response
                # ------------------------------------------------

                st.markdown(final_response)


                # ------------------------------------------------
                # Save response
                # ------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": final_response
                    }
                )


            # ----------------------------------------------------
            # Error handling
            # ----------------------------------------------------

            except Exception as e:

                error_message = (
                    "An error occurred while processing "
                    "your request.\n\n"
                    f"`{str(e)}`"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )