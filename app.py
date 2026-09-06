import streamlit as st
import requests


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Developer Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# API CONFIGURATION
# ============================================================

API_URL = "https://ai-developer-assistant-0kbj.onrender.com/chat"


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
    # Send request to Render API
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Processing your request..."):

            try:

                response = requests.post(
                    API_URL,
                    json={
                        "message": user_input
                    },
                    timeout=120
                )


                # ------------------------------------------------
                # Check API response
                # ------------------------------------------------

                response.raise_for_status()


                # ------------------------------------------------
                # Get JSON response
                # ------------------------------------------------

                data = response.json()


                # ------------------------------------------------
                # Extract assistant response
                # ------------------------------------------------

                final_response = data.get(
                    "response",
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
            # API error
            # ----------------------------------------------------

            except requests.exceptions.Timeout:

                error_message = (
                    "The request took too long to complete. "
                    "Please try again."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


            # ----------------------------------------------------
            # Connection error
            # ----------------------------------------------------

            except requests.exceptions.ConnectionError:

                error_message = (
                    "Could not connect to the AI Developer "
                    "Assistant API."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


            # ----------------------------------------------------
            # API returned an error
            # ----------------------------------------------------

            except requests.exceptions.HTTPError:

                try:
                    error_detail = response.json().get(
                        "detail",
                        "Unknown API error."
                    )
                except Exception:
                    error_detail = response.text

                error_message = (
                    f"API Error: {error_detail}"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )


            # ----------------------------------------------------
            # Other errors
            # ----------------------------------------------------

            except Exception as e:

                error_message = (
                    "An unexpected error occurred.\n\n"
                    f"`{str(e)}`"
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message
                    }
                )